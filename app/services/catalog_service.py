
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.product import Product
from app.models.product_unit import ProductUnit
from app.models.category import Category
from app.models.producer import Producer
from app.models.product_review import ProductReview


def get_catalog_products(db: Session):
    products = (
        db.query(Product, Category, Producer)
        .join(Category, Product.category_id == Category.id)
        .join(Producer, Product.producer_id == Producer.id)
        .filter(
            Product.is_active == True,
            Category.is_active == True
        )
        .order_by(Product.name.asc())
        .all()
    )

    # Ambil rata-rata rating dan jumlah ulasan semua produk
    review_stats = (
        db.query(
            ProductReview.product_id,
            func.avg(ProductReview.rating).label("average_rating"),
            func.count(ProductReview.id).label("review_count")
        )
        .group_by(ProductReview.product_id)
        .all()
    )

    # Ubah hasil query menjadi dictionary agar mudah digunakan
    review_data = {
        product_id: {
            "average_rating": float(average_rating),
            "review_count": review_count
        }
        for product_id, average_rating, review_count in review_stats
    }

    result = []

    for product, category, producer in products:
        units = db.query(ProductUnit).filter(
            ProductUnit.product_id == product.id,
            ProductUnit.is_active == True
        ).all()

        # Ambil rating produk
        rating_info = review_data.get(product.id, {
            "average_rating": 0,
            "review_count": 0
        })

        result.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "image": product.image,
            "category": category.name,
            "base_unit": product.base_unit,
            "stock_quantity": product.stock_quantity,

            "average_rating": rating_info["average_rating"],
            "review_count": rating_info["review_count"],

            "producer": {
                "id": producer.id,
                "shop_name": producer.shop_name,
                "market_name": producer.market_name,
                "block": producer.block,
                "stall_number": producer.stall_number,
                "floor": producer.floor
            },

            "units": [
                {
                    "id": unit.id,
                    "unit_name": unit.unit_name,
                    "conversion_factor": unit.conversion_factor,
                    "price": unit.price
                }
                for unit in units
            ]
        })

    return result
