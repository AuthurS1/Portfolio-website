// Hiện thông báo khi thêm task
document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".todo-form");
    const message = document.createElement("div");
    message.className = "message";
    document.body.prepend(message);

    form.addEventListener("submit", () => {
        message.textContent = "✅ Task Added!";
        message.style.display = "block";
        setTimeout(() => {
            message.style.display = "none";
        }, 2000);
    });

    // Xác nhận trước khi xóa
    const deleteLinks = document.querySelectorAll(".delete");
    deleteLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            if (!confirm("Bạn có chắc muốn xóa task này không?")) {
                e.preventDefault();
            }
        });
    });

    // Lọc theo priority
    const filter = document.createElement("select");
    filter.innerHTML = `
        <option value="all">All</option>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
    `;
    filter.className = "filter";
    document.querySelector(".container h1").after(filter);

    filter.addEventListener("change", () => {
        const value = filter.value;
        document.querySelectorAll(".todo-list li").forEach(li => {
            if (value === "all" || li.querySelector(".priority").classList.contains(value)) {
                li.style.display = "flex";
            } else {
                li.style.display = "none";
            }
        });
    });
});
