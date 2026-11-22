
const searchInput = document.getElementById("searchInput");
const productCards = document.querySelectorAll(".product-card");
const noResults = document.getElementById("noResults");


// ==========================================
// PENCARIAN PRODUK
// ==========================================

searchInput.addEventListener("input", function () {

    const keyword = this.value.toLowerCase();
    let visibleCount = 0;

    productCards.forEach(card => {

        const name = card.dataset.name;
        const shop = card.dataset.shop;
        const category = card.dataset.category;

        const match =
            name.includes(keyword) ||
            shop.includes(keyword) ||
            category.includes(keyword);

        card.style.display = match ? "" : "none";

        if (match) {
            visibleCount++;
        }

    });

    noResults.hidden = visibleCount !== 0;

});


// ==========================================
// MENGUBAH HARGA BERDASARKAN SATUAN
// ==========================================

document.querySelectorAll(".unit-select").forEach(select => {

    select.addEventListener("change", function () {

        const selectedOption = this.options[this.selectedIndex];
        const price = Number(selectedOption.dataset.price);

        const priceElement = this
            .closest(".product-info")
            .querySelector(".price-value");

        priceElement.textContent = new Intl.NumberFormat("id-ID")
            .format(price);

    });

});


// ==========================================
// MENAMBAHKAN PRODUK KE KERANJANG
// ==========================================

document.querySelectorAll(".add-cart-btn").forEach(button => {

    button.addEventListener("click", async function () {

        const productInfo = this.closest(".product-info");

        const unitSelect = productInfo.querySelector(".unit-select");

        if (!unitSelect || !unitSelect.value) {

            alert("Satuan produk belum tersedia.");

            return;

        }

        const productUnitId = Number(unitSelect.value);

        const originalText = this.textContent;

        this.disabled = true;
        this.textContent = "Menambahkan...";

        try {

            const response = await fetch("/customer/cart/items", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    product_unit_id: productUnitId,
                    quantity: 1

                })

            });

            const result = await response.json();

            if (!response.ok) {

                throw new Error(
                    result.detail || "Gagal menambahkan produk."
                );

            }

            alert("Produk berhasil ditambahkan ke keranjang!");

        } catch (error) {

            alert(error.message);

        } finally {

            this.disabled = false;
            this.textContent = originalText;

        }

    });

});
