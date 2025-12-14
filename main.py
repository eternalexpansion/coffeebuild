from typing import Tuple, Optional
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CoffeeOrder:
    base: str
    size: str
    milk: str = "none"
    syrups: Tuple[str, ...] = field(default_factory=tuple)
    sugar: int = 0
    iced: bool = False
    price: float = 0.0
    description: str = ""
    
    def __str__(self) -> str:
        return self.description if self.description else f"Coffee order: {self.price:.2f} руб."


class CoffeeOrderBuilder:
    """
    билдер для создания заказов кофе с валидацией.
    
    правила итд:
    - обязательные поля base и size
    - лимит сахара: 0-5 ложек
    - сиропов максимум 4
    - цены и множители:
        база цены: espresso=200, americano=250, latte=300, cappuccino=320
        размер: small=1.0, medium=1.2, large=1.4
        доплатп за молоко: whole/skim=30, oat=60, soy=50, none=0
        сироп: 40 за каждый
        лед: 0.2 фиксированно
    """
    BASE_PRICES = {
        "espresso": 200.0,
        "americano": 250.0,
        "latte": 300.0,
        "cappuccino": 320.0
    }
    
    SIZE_MULTIPLIERS = {
        "small": 1.0,
        "medium": 1.2,
        "large": 1.4
    }
    
    MILK_PRICES = {
        "none": 0.0,
        "whole": 30.0,
        "skim": 30.0,
        "oat": 60.0,
        "soy": 50.0
    }
    
    SYRUP_PRICE = 40.0
    ICED_PRICE = 0.2
    MAX_SUGAR = 5
    MAX_SYRUPS = 4
    
    VALID_BASES = {"espresso", "americano", "latte", "cappuccino"}
    VALID_SIZES = {"small", "medium", "large"}
    VALID_MILKS = {"none", "whole", "skim", "oat", "soy"}
    
    def __init__(self) -> None:
        self.clear_extras()
        self._base: Optional[str] = None
        self._size: Optional[str] = None
    
    def set_base(self, base: str) -> "CoffeeOrderBuilder":
	    if base not in self.VALID_BASES:
            raise ValueError(f"Invalid base: {base}. Must be one of {self.VALID_BASES}")
        self._base = base
        return self
    
    def set_size(self, size: str) -> "CoffeeOrderBuilder":
        if size not in self.VALID_SIZES:
            raise ValueError(f"invalid size: {size}. must be one of {self.VALID_SIZES}")
        self._size = size
        return self
    
    def set_milk(self, milk: str) -> "CoffeeOrderBuilder":
        if milk not in self.VALID_MILKS:
            raise ValueError(f"invalid milk type: {milk}. must be one of {self.VALID_MILKS}")
        self._milk = milk
        return self
    
    def add_syrup(self, name: str) -> "CoffeeOrderBuilder":
        if len(self._syrups) >= self.MAX_SYRUPS:
            raise ValueError(f"cannot add more than {self.MAX_SYRUPS} syrups")
        
        if name not in self._syrups:
            self._syrups = self._syrups + (name,)
        return self
    
    def set_sugar(self, teaspoons: int) -> "CoffeeOrderBuilder":
        if not 0 <= teaspoons <= self.MAX_SUGAR:
            raise ValueError(f"sugar quantity must be between 0 and {self.MAX_SUGAR}")
        self._sugar = teaspoons
        return self
    
    def set_iced(self, iced: bool = True) -> "CoffeeOrderBuilder":
        self._iced = iced
        return self
    
    def clear_extras(self) -> "CoffeeOrderBuilder":
        self._milk = "none"
        self._syrups: Tuple[str, ...] = ()
        self._sugar = 0
        self._iced = False
        return self
    
    def _calculate_price(self) -> float:
        if self._base is None or self._size is None:
            raise ValueError("base and size must be set before calculating price")
        
        base_price = self.BASE_PRICES[self._base]
        size_multiplier = self.SIZE_MULTIPLIERS[self._size]
        price = base_price * size_multiplier
        
        price += self.MILK_PRICES[self._milk]
        price += len(self._syrups) * self.SYRUP_PRICE
        if self._iced:
            price += self.ICED_PRICE
            
        return price
    
    def _build_description(self) -> str:
        if self._base is None or self._size is None:
            return ""
        
        parts = [f"{self._size} {self._base}"]
        if self._milk != "none":
            parts.append(f"with {self._milk} milk")
        
        if self._syrups:
            syrup_list = "+".join(self._syrups)
            parts.append(f"+{syrup_list}")
        
        if self._iced:
            parts.append("(iced)")
        
        if self._sugar > 0:
            parts.append(f"{self._sugar} tsp sugar")
        
        return " ".join(parts)
    
    def build(self) -> CoffeeOrder:
        if self._base is None:
            raise ValueError("base is required")
        if self._size is None:
            raise ValueError("size is required")
        if len(self._syrups) > self.MAX_SYRUPS:
            raise ValueError(f"cannot have more than {self.MAX_SYRUPS} syrups")
        if not 0 <= self._sugar <= self.MAX_SUGAR:
            raise ValueError(f"sugar quantity must be between 0 and {self.MAX_SUGAR}")
        price = self._calculate_price()
        description = self._build_description()
        
        order = CoffeeOrder(
            base=self._base,
            size=self._size,
            milk=self._milk,
            syrups=self._syrups,
            sugar=self._sugar,
            iced=self._iced,
            price=price,
            description=description
        )
        
        return order


def test_coffee_order_builder() -> None:
    builder = CoffeeOrderBuilder()
    order1 = builder.set_base("latte").set_size("medium").build()
    
    assert isinstance(order1, CoffeeOrder)
    assert order1.base == "latte"
    assert order1.size == "medium"
    assert order1.milk == "none"
    assert order1.sugar == 0
    assert not order1.iced
    assert order1.syrups == ()
    assert order1.price > 0
    assert "medium latte" in order1.description
    print("base order: ok")
    
    order2 = (builder.set_base("cappuccino")
              .set_size("large")
              .set_milk("oat")
              .add_syrup("vanilla")
              .add_syrup("caramel")
              .set_sugar(2)
              .set_iced(True)
              .build())
    
    assert order2.base == "cappuccino"
    assert order2.size == "large"
    assert order2.milk == "oat"
    assert order2.sugar == 2
    assert order2.iced
    assert len(order2.syrups) == 2
    assert "vanilla" in order2.syrups
    assert "caramel" in order2.syrups
    assert "oat milk" in order2.description.lower()
    assert "vanilla+caramel" in order2.description
    assert "2 tsp sugar" in order2.description
    print("include order addons: ok")
    
    order3 = builder.set_base("americano").set_size("small").set_sugar(1).build()
    
    assert order3.base == "americano"
    assert order3.size == "small"
    assert order3.sugar == 1
    assert order2.base == "cappuccino"
    assert order2.size == "large"
    assert order2.sugar == 2
    print("builder reuse: ok")
    
    builder2 = CoffeeOrderBuilder()
    try:
        builder2.set_size("medium").build()
        assert False, "raise ValueError for missing base"
    except ValueError as e:
        assert "base is required" in str(e)
        print("missing base validation: ok")
    
    builder3 = CoffeeOrderBuilder()
    try:
        builder3.set_base("espresso").build()
        assert False, "raise ValueError for missing size"
    except ValueError as e:
        assert "size is required" in str(e)
        print("missing size validation: ok")
    
    builder4 = CoffeeOrderBuilder()
    try:
        builder4.set_base("latte").set_size("medium").set_sugar(10)
        assert False, "raise ValueError for too much sugar"
    except ValueError as e:
        assert "sugar quantity must be between 0 and 5" in str(e)
        print("syrup limit validation: ok")
    
    builder5 = CoffeeOrderBuilder()
    builder5.set_base("latte").set_size("medium")
    for i in range(5):
        builder5.add_syrup(f"syrup{i}")
    try:
        builder5.build()
        assert False, "raise ValueError for too many syrups"
    except ValueError as e:
        assert "cannot have more than 4 syrups" in str(e)
        print("syrup limit validation: ok")
    
    builder6 = CoffeeOrderBuilder()
    order6 = (builder6.set_base("latte")
              .set_size("medium")
              .add_syrup("vanilla")
              .add_syrup("vanilla")
              .add_syrup("vanilla")
              .build())
    
    assert len(order6.syrups) == 1  
    assert order6.price == 300 * 1.2 + 40  
    print("dismiss syrup dupes: ok")
    
    builder7 = CoffeeOrderBuilder()
    order7_no_ice = builder7.set_base("americano").set_size("small").build()
    order7_ice = builder7.set_iced(True).build()
    
    assert order7_ice.price - order7_no_ice.price == CoffeeOrderBuilder.ICED_PRICE
    print("ice add. fee: ok")
    
    builder8 = CoffeeOrderBuilder()
    order8_with_extras = (builder8.set_base("latte")
                          .set_size("medium")
                          .set_milk("soy")
                          .add_syrup("chocolate")
                          .set_sugar(3)
                          .set_iced(True)
                          .build())
    
    order8_cleared = builder8.clear_extras().set_base("espresso").set_size("small").build()
    
    assert order8_cleared.milk == "none"
    assert order8_cleared.syrups == ()
    assert order8_cleared.sugar == 0
    assert not order8_cleared.iced
    print("clear extras: ok")
    
    builder9 = CoffeeOrderBuilder()
    order9 = (builder9.set_base("cappuccino")
              .set_size("large")
              .set_milk("whole")
              .add_syrup("hazelnut")
              .set_iced(True)
              .build())
    
    description = order9.description.lower()
    assert "large cappuccino" in description
    assert "with whole milk" in description
    assert "+hazelnut" in description
    assert "(iced)" in description
    assert "tsp sugar" not in description
    print("order desc: ok")
    
    print("tests passed")


if __name__ == "__main__":
    test_coffee_order_builder()