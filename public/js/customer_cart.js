
// ==========================================
// TOMBOL TAMBAH DAN KURANGI JUMLAH
// ==========================================

document.querySelectorAll(".cart-item").forEach(cartItem => {

    const quantityInput = cartItem.querySelector(".cart-quantity");

    const minusButton = cartItem.querySelector(".quantity-minus");
    const plusButton = cartItem.querySelector(".quantity-plus");

    // Mengurangi jumlah sebanyak 1
    minusButton.addEventListener("click", function () {

        let quantity = Number(quantityInput.value);

        if (!Number.isFinite(quantity)) {
            quantity = 1;
        }

        quantity = Math.max(0.001, quantity - 1);

        quantityInput.value = Number(quantity.toFixed(3));

    });

    // Menambah jumlah sebanyak 1
    plusButton.addEventListener("click", function () {

        let quantity = Number(quantityInput.value);

        if (!Number.isFinite(quantity) || quantity < 0.001) {
            quantity = 0;
        }

        quantity += 1;

        quantityInput.value = Number(quantity.toFixed(3));

    });

});


// ==========================================
// UPDATE JUMLAH PRODUK
// ==========================================

document.querySelectorAll(".update-cart-btn").forEach(button => {

    button.addEventListener("click", async function () {

        const cartItem = this.closest(".cart-item");
        const itemId = cartItem.dataset.itemId;

        const quantityInput = cartItem.querySelector(".cart-quantity");
        const quantity = Number(quantityInput.value);

        if (!Number.isFinite(quantity) || quantity <= 0) {

            alert("Jumlah produk harus lebih dari 0.");

            return;

        }

        this.disabled = true;
        this.textContent = "Memproses...";

        try {

            const response = await fetch(
                `/customer/cart/items/${itemId}`,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        quantity: quantity
                    })
                }
            );

            const result = await response.json();

            if (!response.ok) {

                throw new Error(
                    result.detail || "Gagal mengubah jumlah produk."
                );

            }

            alert("Jumlah produk berhasil diperbarui.");

            window.location.reload();

        } catch (error) {

            alert(error.message);

        } finally {

            this.disabled = false;
            this.textContent = "Update";

        }

    });

});


// ==========================================
// HAPUS PRODUK DARI KERANJANG
// ==========================================

document.querySelectorAll(".delete-cart-btn").forEach(button => {

    button.addEventListener("click", async function () {

        const cartItem = this.closest(".cart-item");
        const itemId = cartItem.dataset.itemId;

        const confirmation = confirm(
            "Apakah kamu yakin ingin menghapus produk ini?"
        );

        if (!confirmation) {
            return;
        }

        this.disabled = true;
        this.textContent = "Menghapus...";

        try {

            const response = await fetch(
                `/customer/cart/items/${itemId}`,
                {
                    method: "DELETE"
                }
            );

            const result = await response.json();

            if (!response.ok) {

                throw new Error(
                    result.detail || "Gagal menghapus produk."
                );

            }

            alert("Produk berhasil dihapus dari keranjang.");

            window.location.reload();

        } catch (error) {

            alert(error.message);

        } finally {

            this.disabled = false;
            this.textContent = "Hapus";

        }

    });

});
