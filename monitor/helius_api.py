"""
Helius API Integration for Solana Token Analysis
Provides functions to analyze tokens and extract early bidder data
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import base58
import re
from debug_config import is_debug_enabled

# ============================================================================
# OPSEC: PRODUCTION MODE - Disable Sensitive Logging
# ============================================================================
# Debug logging is controlled by debug_config.py - change DEBUG_MODE there
# ============================================================================

def safe_print(*args, **kwargs):
    """Only print if debug mode is enabled in debug_config.py"""
    if is_debug_enabled():
        print(*args, **kwargs)

# Replace built-in print with safe version
print = safe_print
# ============================================================================

class HeliusAPI:
    """Wrapper for Helius RPC and Enhanced API endpoints"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.rpc_url = f"https://mainnet.helius-rpc.com/?api-key={api_key}"
        self.enhanced_url = "https://api.helius.xyz/v0"
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def is_wallet_on_curve(self, wallet_address: str) -> bool:
        """
        Check if a wallet address is on-curve using Solana's PublicKey validation.
        On-curve addresses are valid ed25519 curve points that can sign transactions.
        """
        try:
            # Use base58 to decode and validate the address
            decoded = base58.b58decode(wallet_address)
            # Solana addresses are 32 bytes
            if len(decoded) != 32:
                return False
            # If it decodes properly and is 32 bytes, it's on-curve
            return True
        except Exception:
            return False

    def _rpc_call(self, method: str, params: list) -> dict:
        """Make a JSON-RPC call to Helius"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        try:
            response = self.session.post(self.rpc_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            if 'error' in result:
                raise Exception(f"RPC Error: {result['error']}")
            return result.get('result', {})
        except Exception as e:
            raise Exception(f"RPC call failed: {str(e)}")

    def _enhanced_call(self, endpoint: str, params: dict) -> dict:
        """Make a call to Helius Enhanced API"""
        url = f"{self.enhanced_url}/{endpoint}"
        params['api-key'] = self.api_key
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Enhanced API call failed: {str(e)}")

    def get_token_metadata(self, mint_address: str) -> Optional[Dict]:
        """Get token metadata including name, symbol, etc."""
        try:
            # Try the regular token metadata endpoint first
            result = self._enhanced_call('token-metadata', {
                'mintAccounts': mint_address
            })
            if result and result[0]:
                return result[0]
        except Exception as e:
            print(f"Error fetching token metadata (standard): {str(e)}")

        # For pump.fun tokens, try DAS API (Digital Asset Standard)
        try:
            print("[Helius] Trying DAS API for token metadata...")
            payload = {
                "jsonrpc": "2.0",
                "id": "token-metadata",
                "method": "getAsset",
                "params": {
                    "id": mint_address,
                    "displayOptions": {
                        "showUnverifiedCollections": True,
                        "showCollectionMetadata": True
                    }
                }
            }
            response = self.session.post(self.rpc_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if 'result' in result and result['result']:
                asset = result['result']
                # Extract name and symbol from DAS response
                content = asset.get('content', {})
                metadata = content.get('metadata', {})

                token_name = metadata.get('name') or content.get('json_uri', 'Unknown')
                token_symbol = metadata.get('symbol', 'UNK')

                print(f"[Helius] DAS API found: {token_name} ({token_symbol})")

                # Format it similar to standard metadata response
                return {
                    'onChainMetadata': {
                        'metadata': {
                            'name': token_name,
                            'symbol': token_symbol
                        }
                    },
                    'legacyMetadata': metadata
                }
        except Exception as das_error:
            print(f"Error fetching token metadata (DAS): {str(das_error)}")

        return None

    def get_parsed_transactions(self, address: str, limit: int = 100) -> List[Dict]:
        """
        Get parsed transaction history for an address.
        Returns transactions with decoded swap/transfer data.
        """
        try:
            # Get transaction signatures first
            signatures = self._rpc_call('getSignaturesForAddress', [
                address,
                {"limit": limit}
            ])

            if not signatures:
                return []

            sig_list = [sig['signature'] for sig in signatures[:limit]]
            print(f"[Helius] Fetching details for {len(sig_list)} transactions...")

            # Fetch transactions individually using RPC method
            # This is more reliable than the Enhanced API batch endpoint
            all_transactions = []

            for i, signature in enumerate(sig_list):
                if i % 50 == 0:  # Progress indicator every 50 transactions
                    print(f"[Helius] Progress: {i}/{len(sig_list)} transactions fetched...")

                try:
                    # Use getTransaction RPC method with maxSupportedTransactionVersion
                    tx_data = self._rpc_call('getTransaction', [
                        signature,
                        {
                            "encoding": "jsonParsed",
                            "maxSupportedTransactionVersion": 0
                        }
                    ])

                    if tx_data:
                        # Extract relevant transaction info
                        parsed_tx = self._parse_rpc_transaction(tx_data, signature)
                        if parsed_tx:
                            all_transactions.append(parsed_tx)

                except Exception as tx_error:
                    # Skip individual transaction errors
                    continue

            print(f"[Helius] Total transactions retrieved: {len(all_transactions)}")
            return all_transactions

        except Exception as e:
            print(f"Error fetching parsed transactions: {str(e)}")
            return []

    def _parse_rpc_transaction(self, tx_data: dict, signature: str) -> dict:
        """
        Parse RPC transaction data into a simplified format.
        Extracts timestamp, type, transfers, etc.
        Also tries to extract token metadata from parsed account data.
        """
        try:
            # Extract block time (timestamp)
            timestamp = tx_data.get('blockTime')

            # Extract transaction details
            transaction = tx_data.get('transaction', {})
            meta = tx_data.get('meta', {})

            # Try to extract token info from parsed account data
            token_metadata = {}
            message = transaction.get('message', {})
            for instruction in message.get('instructions', []):
                if isinstance(instruction, dict):
                    parsed = instruction.get('parsed')
                    if parsed and isinstance(parsed, dict):
                        # Look for token info in parsed instructions
                        info = parsed.get('info', {})
                        if 'mint' in info:
                            token_metadata['mint'] = info['mint']

            # Parse token transfers from meta
            token_transfers = []
            if 'postTokenBalances' in meta and 'preTokenBalances' in meta:
                pre_balances = {b['accountIndex']: b for b in meta.get('preTokenBalances', [])}
                post_balances = {b['accountIndex']: b for b in meta.get('postTokenBalances', [])}

                for account_index, post_bal in post_balances.items():
                    pre_bal = pre_balances.get(account_index, {})

                    # Handle None values from uiAmount
                    pre_ui_amount = pre_bal.get('uiTokenAmount', {}).get('uiAmount')
                    post_ui_amount = post_bal.get('uiTokenAmount', {}).get('uiAmount')

                    # If uiAmount is None, use the raw amount divided by decimals
                    if pre_ui_amount is None:
                        pre_amount_raw = float(pre_bal.get('uiTokenAmount', {}).get('amount', 0))
                        pre_decimals = int(pre_bal.get('uiTokenAmount', {}).get('decimals', 0))
                        pre_amount = pre_amount_raw / (10 ** pre_decimals) if pre_decimals > 0 else pre_amount_raw
                    else:
                        pre_amount = float(pre_ui_amount)

                    if post_ui_amount is None:
                        post_amount_raw = float(post_bal.get('uiTokenAmount', {}).get('amount', 0))
                        post_decimals = int(post_bal.get('uiTokenAmount', {}).get('decimals', 0))
                        post_amount = post_amount_raw / (10 ** post_decimals) if post_decimals > 0 else post_amount_raw
                    else:
                        post_amount = float(post_ui_amount)

                    if pre_amount != post_amount:
                        # Get account addresses
                        accounts = transaction.get('message', {}).get('accountKeys', [])
                        if account_index < len(accounts):
                            account_key = accounts[account_index]
                            if isinstance(account_key, dict):
                                account_address = account_key.get('pubkey')
                            else:
                                account_address = account_key

                            token_transfers.append({
                                'mint': post_bal.get('mint'),
                                'toUserAccount': account_address if post_amount > pre_amount else None,
                                'fromUserAccount': account_address if post_amount < pre_amount else None,
                                'tokenAmount': abs(post_amount - pre_amount)
                            })

            # Parse native (SOL) transfers
            native_transfers = []
            if 'preBalances' in meta and 'postBalances' in meta:
                accounts = transaction.get('message', {}).get('accountKeys', [])
                pre_balances = meta.get('preBalances', [])
                post_balances = meta.get('postBalances', [])

                for i, (pre_bal, post_bal) in enumerate(zip(pre_balances, post_balances)):
                    if pre_bal != post_bal and i < len(accounts):
                        account_key = accounts[i]
                        if isinstance(account_key, dict):
                            account_address = account_key.get('pubkey')
                        else:
                            account_address = account_key

                        native_transfers.append({
                            'fromUserAccount': account_address if post_bal < pre_bal else None,
                            'toUserAccount': account_address if post_bal > pre_bal else None,
                            'amount': abs(post_bal - pre_bal)
                        })

            return {
                'signature': signature,
                'timestamp': timestamp,
                'type': 'UNKNOWN',  # We'll infer type from transfers
                'tokenTransfers': token_transfers,
                'nativeTransfers': native_transfers
            }

        except Exception as e:
            return None

    def analyze_token_early_bidders(
        self,
        mint_address: str,
        min_usd: float = 50.0,
        time_window_hours: int = 24,
        max_transactions: int = 500
    ) -> Dict:
        """
        Analyze a token to find early bidders.

        Args:
            mint_address: Token mint address to analyze
            min_usd: Minimum USD amount to consider (default: $50)
            time_window_hours: Hours from first transaction to consider (default: 24)
            max_transactions: Maximum transactions to analyze (default: 500)

        Returns:
            Dictionary with analysis results:
            {
                'token_address': str,
                'token_info': dict,
                'first_transaction_time': datetime,
                'analysis_window_end': datetime,
                'early_bidders': [
                    {
                        'wallet_address': str,
                        'first_buy_time': datetime,
                        'total_usd': float,
                        'transaction_count': int,
                        'average_buy_usd': float
                    }
                ],
                'total_unique_buyers': int,
                'total_transactions_analyzed': int
            }
        """
        print(f"[Helius] Analyzing token: {mint_address}")

        # Get token metadata
        token_info = self.get_token_metadata(mint_address)
        if token_info:
            token_name = token_info.get('onChainMetadata', {}).get('metadata', {}).get('name', 'Unknown')
            print(f"[Helius] Token info: {token_name}")
        else:
            print(f"[Helius] Token info: Unknown (metadata not available)")

        # Get transaction history
        print(f"[Helius] Fetching up to {max_transactions} transactions...")
        transactions = self.get_parsed_transactions(mint_address, limit=max_transactions)
        print(f"[Helius] Retrieved {len(transactions)} transactions")

        if not transactions:
            return {
                'token_address': mint_address,
                'token_info': token_info,
                'error': 'No transactions found',
                'early_bidders': [],
                'total_unique_buyers': 0,
                'total_transactions_analyzed': 0
            }

        # Find first transaction timestamp
        first_tx_time = None
        for tx in reversed(transactions):  # Oldest first
            if tx.get('timestamp'):
                first_tx_time = datetime.fromtimestamp(tx['timestamp'])
                break

        if not first_tx_time:
            return {
                'token_address': mint_address,
                'token_info': token_info,
                'error': 'Could not determine first transaction time',
                'early_bidders': [],
                'total_unique_buyers': 0,
                'total_transactions_analyzed': 0
            }

        window_end = first_tx_time + timedelta(hours=time_window_hours)
        print(f"[Helius] Analysis window: {first_tx_time} to {window_end}")

        # Track buyers within time window
        buyers = {}  # wallet_address -> {first_buy, total_usd, tx_count}

        # Debug: Track what we're seeing
        total_checked = 0
        within_window = 0
        has_buyer = 0
        meets_threshold = 0
        debug_first_done = False

        for tx in transactions:
            if not tx.get('timestamp'):
                continue

            total_checked += 1

            tx_time = datetime.fromtimestamp(tx['timestamp'])

            # Skip transactions outside time window
            if tx_time > window_end:
                continue

            within_window += 1

            # Parse transaction for swap/buy activity (debug first one)
            buyer_wallet, usd_amount = self._extract_buy_info(tx, mint_address, debug_first=not debug_first_done)
            if not debug_first_done:
                debug_first_done = True

            if buyer_wallet and usd_amount:
                has_buyer += 1

                # CRITICAL: Only include on-curve wallets (wallets that can sign transactions)
                if not self.is_wallet_on_curve(buyer_wallet):
                    if not debug_first_done:
                        print(f"[Helius] Skipping off-curve wallet: {buyer_wallet}")
                    continue

                if usd_amount >= min_usd:
                    meets_threshold += 1

                    if buyer_wallet not in buyers:
                        buyers[buyer_wallet] = {
                            'wallet_address': buyer_wallet,
                            'first_buy_time': tx_time,
                            'total_usd': 0.0,
                            'transaction_count': 0
                        }

                    buyers[buyer_wallet]['total_usd'] += usd_amount
                    buyers[buyer_wallet]['transaction_count'] += 1

                    # Keep earliest buy time
                    if tx_time < buyers[buyer_wallet]['first_buy_time']:
                        buyers[buyer_wallet]['first_buy_time'] = tx_time

        print(f"[Helius] Debug: Checked {total_checked} txs, {within_window} in window, {has_buyer} with buyers, {meets_threshold} meeting threshold")

        # Convert to sorted list (earliest buyers first)
        early_bidders = list(buyers.values())
        for bidder in early_bidders:
            bidder['average_buy_usd'] = bidder['total_usd'] / bidder['transaction_count']

        early_bidders.sort(key=lambda x: x['first_buy_time'])

        print(f"[Helius] Found {len(early_bidders)} early bidders (>${min_usd} USD)")

        return {
            'token_address': mint_address,
            'token_info': token_info,
            'first_transaction_time': first_tx_time.isoformat(),
            'analysis_window_end': window_end.isoformat(),
            'early_bidders': early_bidders,
            'total_unique_buyers': len(early_bidders),
            'total_transactions_analyzed': len(transactions)
        }

    def _extract_buy_info(self, tx: dict, mint_address: str, debug_first: bool = False) -> tuple:
        """
        Extract buyer wallet and USD amount from a parsed transaction.
        Returns: (wallet_address, usd_amount) or (None, None)

        For pump.fun tokens, we use SOL amount spent as a proxy for USD value.
        1 SOL ≈ $200 USD (adjust based on current market price)

        IMPORTANT: Token transfers show the associated token account (ATA), but SOL payments
        come from the main wallet. We need to find the largest SOL sender in the transaction
        as the buyer (they're paying for the tokens).
        """
        try:
            native_transfers = tx.get('nativeTransfers', [])
            token_transfers = tx.get('tokenTransfers', [])

            if debug_first:
                print(f"[Debug] Transaction has {len(token_transfers)} token transfers, {len(native_transfers)} native transfers")
                if token_transfers:
                    print(f"[Debug] First token transfer: {token_transfers[0]}")
                if native_transfers:
                    print(f"[Debug] First native transfer: {native_transfers[0]}")

            # Find if someone bought this token (received the token)
            for transfer in token_transfers:
                if transfer.get('mint') == mint_address:
                    # Check if someone received this token (buy)
                    token_recipient = transfer.get('toUserAccount')

                    if debug_first:
                        print(f"[Debug] Found matching mint, token recipient: {token_recipient}")

                    if not token_recipient:
                        continue

                    # NEW APPROACH: Find the wallet that sent SOL in this transaction
                    # Since pump.fun swaps involve sending SOL to get tokens, the buyer
                    # is whoever sent the largest amount of SOL in this transaction

                    largest_sol_payment = 0
                    buyer_wallet = None

                    if debug_first:
                        print(f"[Debug] Looking for SOL payments in {len(native_transfers)} native transfers")

                    for native in native_transfers:
                        sender = native.get('fromUserAccount')
                        receiver = native.get('toUserAccount')
                        amount = native.get('amount', 0)

                        if debug_first:
                            print(f"[Debug] Native transfer: from={sender}, to={receiver}, amount={amount} lamports ({amount/1e9:.4f} SOL)")

                        # Skip if no sender (e.g., rent refunds)
                        if not sender:
                            continue

                        # The buyer is the one sending SOL (not receiving)
                        # Also, ignore very small amounts (< 0.0001 SOL) as they're likely fees
                        if amount > 100000 and amount > largest_sol_payment:  # > 0.0001 SOL
                            largest_sol_payment = amount
                            buyer_wallet = sender
                            if debug_first:
                                print(f"[Debug] New largest SOL sender: {sender} with {amount/1e9:.4f} SOL")

                    if buyer_wallet and largest_sol_payment > 0:
                        sol_amount = largest_sol_payment / 1e9
                        usd_amount = sol_amount * 200  # 1 SOL ≈ $200 USD

                        if debug_first:
                            print(f"[Debug] FOUND BUYER! Wallet: {buyer_wallet}, SOL: {sol_amount:.4f}, USD: ${usd_amount:.2f}")

                        return (buyer_wallet, usd_amount)
                    else:
                        if debug_first:
                            print(f"[Debug] No SOL payment found (largest was {largest_sol_payment/1e9:.4f} SOL)")

        except Exception as e:
            # Silently skip parsing errors for individual transactions
            if debug_first:
                print(f"[Debug] Exception in _extract_buy_info: {e}")
            pass

        return (None, None)


def generate_token_acronym(token_name: str, token_symbol: str = None) -> str:
    """
    Generate acronym from token name.

    Examples:
        "Dogecoin Super Mega Moon Edition" → "DSMME"
        "Wrapped SOL" → "WS"
        "Dogecoin" → "DOGE" (first 5 chars if no spaces)
        "AI" → "AI" (keep short names as-is)

    Args:
        token_name: Full token name
        token_symbol: Token symbol (fallback)

    Returns:
        Acronym string
    """
    if not token_name or token_name == "Unknown":
        return token_symbol.upper() if token_symbol else "UNKN"

    # Clean the name
    name = token_name.strip()

    # If name is very short (≤4 chars), use it as-is
    if len(name) <= 4:
        return name.upper()

    # Split by common delimiters (space, hyphen, underscore, dot)
    words = re.split(r'[\s\-_.]+', name)

    # Remove empty strings and common words
    words = [w for w in words if w and w.lower() not in ['the', 'a', 'an', 'of', 'and', 'or']]

    # If we have multiple words, use first letter of each
    if len(words) > 1:
        acronym = ''.join(word[0].upper() for word in words if word)
        return acronym

    # Single word with no spaces - use first 4-5 characters
    if token_symbol and len(token_symbol) <= 5:
        return token_symbol.upper()

    return name[:5].upper()


def generate_axiom_export(
    early_bidders: List[Dict],
    token_name: str,
    token_symbol: str = None,
    limit: int = 10
) -> List[Dict]:
    """
    Generate Axiom wallet tracker import JSON.

    Args:
        early_bidders: List of buyer dictionaries from analysis
        token_name: Token name for acronym generation
        token_symbol: Token symbol (optional)
        limit: Maximum number of wallets (default: 10)

    Returns:
        List of Axiom wallet tracker entries
    """
    acronym = generate_token_acronym(token_name, token_symbol)

    axiom_wallets = []

    for index, bidder in enumerate(early_bidders[:limit], start=1):
        # Round USD amount to whole number
        first_buy_usd = round(bidder.get('total_usd', bidder.get('first_buy_usd', 0)))

        # Format: (1/10)$54|DSMME
        wallet_name = f"({index}/{limit})${first_buy_usd}|{acronym}"

        axiom_entry = {
            "trackedWalletAddress": bidder['wallet_address'],
            "name": wallet_name,
            "emoji": "#️⃣",
            "alertsOnToast": True,
            "alertsOnBubble": True,
            "alertsOnFeed": True,
            "groups": ["Main"],
            "sound": "bing"
        }

        axiom_wallets.append(axiom_entry)

    return axiom_wallets


class TokenAnalyzer:
    """High-level token analysis interface"""

    def __init__(self, api_key: str):
        self.helius = HeliusAPI(api_key)

    def analyze_token(
        self,
        mint_address: str,
        min_usd: float = 50.0,
        time_window_hours: int = 24
    ) -> Dict:
        """
        Analyze a token to find early bidders.

        Args:
            mint_address: Token mint address
            min_usd: Minimum USD threshold (default: $50)
            time_window_hours: Analysis window in hours (default: 24)

        Returns:
            Analysis results dictionary
        """
        return self.helius.analyze_token_early_bidders(
            mint_address=mint_address,
            min_usd=min_usd,
            time_window_hours=time_window_hours
        )


class WebhookManager:
    """Manages Helius webhooks for wallet monitoring"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.webhook_url = "https://api.helius.xyz/v0/webhooks"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        })

    def create_webhook(
        self,
        webhook_url: str,
        wallet_addresses: List[str],
        webhook_type: str = "enhanced",
        transaction_types: List[str] = None
    ) -> Dict:
        """
        Create a new Helius webhook to monitor wallet addresses.

        Args:
            webhook_url: Your server endpoint to receive webhook notifications
            wallet_addresses: List of wallet addresses to monitor
            webhook_type: Type of webhook ("enhanced" or "raw")
            transaction_types: List of transaction types to monitor (e.g., ["TRANSFER", "SWAP"])

        Returns:
            Webhook creation response with webhook_id
        """
        if transaction_types is None:
            transaction_types = ["TRANSFER", "SWAP", "NFT_SALE", "TOKEN_MINT"]

        payload = {
            "webhookURL": webhook_url,
            "transactionTypes": transaction_types,
            "accountAddresses": wallet_addresses,
            "webhookType": webhook_type
        }

        try:
            response = self.session.post(
                f"{self.webhook_url}?api-key={self.api_key}",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            print(f"[Webhook] Created webhook {result.get('webhookID')} for {len(wallet_addresses)} addresses")
            return result
        except Exception as e:
            raise Exception(f"Failed to create webhook: {str(e)}")

    def update_webhook(
        self,
        webhook_id: str,
        wallet_addresses: List[str] = None,
        webhook_url: str = None,
        transaction_types: List[str] = None
    ) -> Dict:
        """
        Update an existing webhook.

        Args:
            webhook_id: ID of the webhook to update
            wallet_addresses: New list of wallet addresses (optional)
            webhook_url: New webhook URL (optional)
            transaction_types: New list of transaction types (optional)

        Returns:
            Update response
        """
        payload = {}
        if wallet_addresses is not None:
            payload["accountAddresses"] = wallet_addresses
        if webhook_url is not None:
            payload["webhookURL"] = webhook_url
        if transaction_types is not None:
            payload["transactionTypes"] = transaction_types

        try:
            response = self.session.put(
                f"{self.webhook_url}/{webhook_id}?api-key={self.api_key}",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            print(f"[Webhook] Updated webhook {webhook_id}")
            return result
        except Exception as e:
            raise Exception(f"Failed to update webhook: {str(e)}")

    def delete_webhook(self, webhook_id: str) -> bool:
        """
        Delete a webhook.

        Args:
            webhook_id: ID of the webhook to delete

        Returns:
            True if successful
        """
        try:
            response = self.session.delete(
                f"{self.webhook_url}/{webhook_id}?api-key={self.api_key}",
                timeout=30
            )
            response.raise_for_status()
            print(f"[Webhook] Deleted webhook {webhook_id}")
            return True
        except Exception as e:
            raise Exception(f"Failed to delete webhook: {str(e)}")

    def get_webhook(self, webhook_id: str) -> Dict:
        """
        Get details of a specific webhook.

        Args:
            webhook_id: ID of the webhook

        Returns:
            Webhook details
        """
        try:
            response = self.session.get(
                f"{self.webhook_url}/{webhook_id}?api-key={self.api_key}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get webhook: {str(e)}")

    def list_webhooks(self) -> List[Dict]:
        """
        List all webhooks for this API key.

        Returns:
            List of webhook objects
        """
        try:
            response = self.session.get(
                f"{self.webhook_url}?api-key={self.api_key}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to list webhooks: {str(e)}")