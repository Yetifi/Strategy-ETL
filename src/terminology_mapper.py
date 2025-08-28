"""
Terminology mapping and normalization for DeFi strategies.
"""
import re
from typing import Dict, List, Tuple, Optional
from .models import StrategyType, AssetType, RiskLevel


class TerminologyMapper:
    """
    Maps generic DeFi terminology to NEAR-specific terms and normalizes language.
    """
    
    def __init__(self):
        # Strategy type mappings
        self.strategy_patterns = {
            StrategyType.YIELD_FARMING: [
                r'\byield\s*farm\w*\b', r'\bfarm\w*\s*yield\b', r'\bharvest\w*\b',
                r'\bapy\b', r'\bapr\b', r'\breturn\w*\b', r'\bprofit\w*\b'
            ],
            StrategyType.LIQUIDITY_PROVIDING: [
                r'\bliquidity\s*provid\w*\b', r'\bprovide\s*liquidity\b', r'\blp\b', r'\bamm\b', r'\bpool\w*\b',
                r'\bswap\w*\b', r'\bdex\b', r'\bexchange\b'
            ],
            StrategyType.LENDING: [
                r'\blend\w*\b', r'\bdeposit\w*\b', r'\binterest\b', r'\bcredit\b',
                r'\bsavings\b', r'\baccount\w*\b'
            ],
            StrategyType.BORROWING: [
                r'\bborrow\w*\b', r'\bloan\w*\b', r'\bdebt\b', r'\bleverage\w*\b',
                r'\bcollateral\b', r'\bunderwater\b'
            ],
            StrategyType.STAKING: [
                r'\bstak\w*\b', r'\bdelegat\w*\b', r'\bvalidator\w*\b', r'\bconsensus\b',
                r'\bproof\s*of\s*stake\b', r'\bpos\b'
            ],
            StrategyType.SWAPPING: [
                r'\bswap\w*\b', r'\btrade\w*\b', r'\bconvert\w*\b', r'\bexchange\w*\b',
                r'\bbuy\w*\b', r'\bsell\w*\b'
            ],
            StrategyType.ARBITRAGE: [
                r'\barbitrage\w*\b', r'\barb\b', r'\bprice\s*difference\b',
                r'\bcross\s*exchange\b', r'\bprofit\s*from\s*difference\b'
            ],
            StrategyType.COMPOUNDING: [
                r'\bcompound\w*\b', r'\breinvest\w*\b', r'\bauto\s*compound\b',
                r'\broll\w*\s*over\b', r'\baccumulate\w*\b'
            ]
        }
        
        # Asset mappings
        self.asset_patterns = {
            AssetType.NEAR: [r'\bnear\b', r'\bprotocol\b', r'\bnative\b'],
            AssetType.USDC: [r'\busdc\b', r'\busd\s*coin\b', r'\bstablecoin\b'],
            AssetType.USDT: [r'\busdt\b', r'\btether\b'],
            AssetType.DAI: [r'\bdai\b', r'\bdecentralized\s*stablecoin\b'],
            AssetType.WBTC: [r'\bwbtc\b', r'\bwrapped\s*bitcoin\b', r'\bbtc\b'],
            AssetType.ETH: [r'\beth\b', r'\bethereum\b'],
            AssetType.SHADE: [r'\bshade\b', r'\bshd\b'],
            AssetType.STNEAR: [r'\bstnear\b', r'\bstaked\s*near\b'],
            AssetType.LINEAR: [r'\blinear\b', r'\blin\b'],
            AssetType.META: [r'\bmeta\b', r'\bmetaverse\b']
        }
        
        # Risk level mappings
        self.risk_patterns = {
            RiskLevel.LOW: [
                r'\blow\s*risk\b', r'\bsafe\b', r'\bconservative\b', r'\bstable\b',
                r'\bblue\s*chip\b', r'\bestablished\b'
            ],
            RiskLevel.MEDIUM: [
                r'\bmedium\s*risk\b', r'\bmoderate\b', r'\bbalanced\b', r'\bstandard\b'
            ],
            RiskLevel.HIGH: [
                r'\bhigh\s*risk\b', r'\baggressive\b', r'\bvolatile\b', r'\bspeculative\b'
            ],
            RiskLevel.VERY_HIGH: [
                r'\bvery\s*high\s*risk\b', r'\bextreme\b', r'\bmaximum\b', r'\brisky\b'
            ]
        }
        
        # NEAR-specific term mappings
        self.near_terms = {
            'yield farming': 'NEAR yield farming',
            'liquidity pool': 'NEAR liquidity pool',
            'liquidity pools': 'NEAR liquidity pools',
            'staking': 'NEAR staking',
            'defi': 'NEAR DeFi',
            'protocol': 'NEAR protocol',
            'blockchain': 'NEAR blockchain',
            'smart contract': 'NEAR smart contract'
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize text by converting to lowercase and removing extra whitespace."""
        return ' '.join(text.lower().split())
    
    def detect_strategy_type(self, text: str) -> Tuple[StrategyType, float]:
        """
        Detect the strategy type from text with confidence score.
        
        Returns:
            Tuple of (StrategyType, confidence_score)
        """
        normalized_text = self.normalize_text(text)
        best_match = None
        best_score = 0.0
        
        for strategy_type, patterns in self.strategy_patterns.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, normalized_text))
            if matches > 0:
                score = min(matches / len(patterns), 1.0)
                if score > best_score:
                    best_score = score
                    best_match = strategy_type
        
        if best_match is None:
            # Default to yield farming if no clear match
            return StrategyType.YIELD_FARMING, 0.3
        
        return best_match, best_score
    
    def detect_assets(self, text: str) -> Tuple[List[AssetType], float]:
        """
        Detect assets mentioned in text with confidence score.
        
        Returns:
            Tuple of (List[AssetType], confidence_score)
        """
        normalized_text = self.normalize_text(text)
        detected_assets = []
        total_matches = 0
        
        for asset_type, patterns in self.asset_patterns.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, normalized_text))
            if matches > 0:
                detected_assets.append(asset_type)
                total_matches += matches
        
        if not detected_assets:
            # Default to NEAR if no assets detected
            detected_assets = [AssetType.NEAR]
            confidence = 0.2
        else:
            confidence = min(total_matches / len(detected_assets), 1.0)
        
        return detected_assets, confidence
    
    def detect_risk_level(self, text: str) -> Tuple[RiskLevel, float]:
        """
        Detect risk level from text with confidence score.
        
        Returns:
            Tuple of (RiskLevel, confidence_score)
        """
        normalized_text = self.normalize_text(text)
        best_match = RiskLevel.MEDIUM  # Default
        best_score = 0.0
        
        for risk_level, patterns in self.risk_patterns.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, normalized_text))
            if matches > 0:
                score = min(matches / len(patterns), 1.0)
                if score > best_score:
                    best_score = score
                    best_match = risk_level
        
        return best_match, best_score
    
    def extract_numerical_values(self, text: str) -> Dict[str, float]:
        """Extract numerical values like APY, duration, etc."""
        # APY/APR patterns
        apy_pattern = r'(\d+(?:\.\d+)?)\s*%?\s*(?:apy|apr|yield|return)'
        duration_pattern = r'(\d+)\s*(?:days?|weeks?|months?|years?)'
        
        apy_match = re.search(apy_pattern, text.lower())
        duration_match = re.search(duration_pattern, text.lower())
        
        result = {}
        if apy_match:
            result['target_apy'] = float(apy_match.group(1))
        if duration_match:
            days = int(duration_match.group(1))
            # Convert to days if other units
            if 'week' in text.lower():
                days *= 7
            elif 'month' in text.lower():
                days *= 30
            elif 'year' in text.lower():
                days *= 365
            result['duration_days'] = days
        
        return result
    
    def map_to_near_terms(self, text: str) -> str:
        """Map generic terms to NEAR-specific terms."""
        result = text
        for generic, near_specific in self.near_terms.items():
            result = re.sub(rf'\b{re.escape(generic)}\b', near_specific, result, flags=re.IGNORECASE)
        return result
    
    def generate_transformation_notes(self, original_text: str, detected_items: Dict) -> List[str]:
        """Generate notes about what was detected and transformed."""
        notes = []
        
        if detected_items.get('strategy_type'):
            notes.append(f"Detected strategy type: {detected_items['strategy_type'].value}")
        
        if detected_items.get('assets'):
            notes.append(f"Detected assets: {', '.join([a.value for a in detected_items['assets']])}")
        
        if detected_items.get('risk_level'):
            notes.append(f"Detected risk level: {detected_items['risk_level'].value}")
        
        if detected_items.get('target_apy'):
            notes.append(f"Extracted target APY: {detected_items['target_apy']}%")
        
        if detected_items.get('duration_days'):
            notes.append(f"Extracted duration: {detected_items['duration_days']} days")
        
        return notes
