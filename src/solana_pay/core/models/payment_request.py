from solana.publickey import PublicKey
from dataclasses import dataclass
from typing import Union, List, Optional, Tuple
from urllib.parse import urlencode, urlparse, parse_qs, ParseResult
from solana_pay.common.utils.helpers import is_null

URL_PROTOCOL = "solana:"


@dataclass
class PaymentRequest:
    recipient: PublicKey
    amount: Optional[float] = None
    spl_token: Optional[PublicKey] = None
    reference: Optional[Union[List[PublicKey], PublicKey]] = None
    label: Optional[str] = None
    message: Optional[str] = None
    memo: Optional[str] = None

    def __post_init__(self):
        if self.amount != None and self.amount < 0:
            raise ValueError("amount cannot be a negative.")

    @classmethod
    def from_url(cls, url: str) -> object:
        try:
            parsed_url: ParseResult = urlparse(url)
            parsed_qs: dict = parse_qs(parsed_url.query)

            for param in parsed_qs.keys():
                if len(parsed_qs[param]) == 1 and param != "reference":
                    parsed_qs.update({param: parsed_qs[param][0]})

            payment_request_args: dict = {
                "recipient": PublicKey(parsed_url.path),
                "amount": float(parsed_qs.get("amount")) if parsed_qs.get("amount") else None,
                "spl_token": PublicKey(parsed_qs.get("spl_token")) if parsed_qs.get("spl_token") else None,
                "reference": [PublicKey(r) for r in parsed_qs.get("reference")] if parsed_qs.get("reference") else None,
                "label": parsed_qs.get("label"),
                "message": parsed_qs.get("message"),
                "memo": parsed_qs.get("memo")
            }
            return cls(**payment_request_args)
        except Exception as e:
            pass

    def __append_reference(self, url_params: List[Tuple[str, str]]) -> None:
        if isinstance(self.reference, list):
            for ref_pub in self.reference:
                url_params.append(("reference", str(ref_pub)))
        else:
            url_params.append(("reference", str(self.reference)))

    def to_url(self) -> str:
        base_url = f"{URL_PROTOCOL}{self.recipient}"
        url_params: List[Tuple[str, str]] = [
            ("amount", str(self.amount)),
            ("spl_token", str(self.spl_token)),
            ("label", self.label),
            ("message", self.message),
            ("memo", self.memo)
        ]
        self.__append_reference(url_params)
        clean_url_params = list(
            filter(lambda x: not is_null(x[1]), url_params))
        url = f"{base_url}?{urlencode(clean_url_params)}"
        return url
