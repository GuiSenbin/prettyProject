"""产品模块 Schema：定义产品搜索、个人产品库和成分分析接口。"""
from pydantic import BaseModel, Field, model_validator


class IngredientItem(BaseModel):
    id: int
    inci_name: str
    zh_name: str
    display_name: str
    aliases: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    description: str | None = None
    safety_level: str | None = None
    purposes: list[str] = Field(default_factory=list)
    position: int | None = None


class ProductSummary(BaseModel):
    id: int
    brand: str | None = None
    name: str
    category: str | None = None
    image_url: str | None = None
    registration_number: str | None = None
    brand_origin_country: str | None = None
    status: str
    source: str
    ingredient_source: str | None = None
    source_url: str | None = None
    has_ingredients: bool
    ingredients: list[IngredientItem] = Field(default_factory=list)
    ingredient_count: int = 0
    benefit_tags: list[str] = Field(default_factory=list)
    risk_tags: list[str] = Field(default_factory=list)


class IngredientGroup(BaseModel):
    name: str
    count: int
    ingredients: list[IngredientItem] = Field(default_factory=list)


class ProductAnalysis(BaseModel):
    status: str
    summary: str
    reasons: list[str] = Field(default_factory=list)
    highlights_text: list[str] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)
    missing_profile_fields: list[str] = Field(default_factory=list)
    highlights: list[IngredientItem] = Field(default_factory=list)


class ProductDetail(BaseModel):
    product: ProductSummary
    analysis: ProductAnalysis
    benefit_groups: list[IngredientGroup] = Field(default_factory=list)
    safety_groups: list[IngredientGroup] = Field(default_factory=list)
    safety_summary: str


class UserProductCreate(BaseModel):
    product_id: int | None = None
    name: str | None = None

    @model_validator(mode="after")
    def validate_target(self):
        if self.product_id is None and not (self.name or "").strip():
            raise ValueError("请选择产品或输入产品名")
        return self


class UserProductResponse(BaseModel):
    id: int
    status: str
    source: str
    custom_name: str | None = None
    product: ProductSummary | None = None
    analysis: ProductAnalysis
    created_at: str | None = None
