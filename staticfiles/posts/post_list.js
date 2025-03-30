document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[id^=toggle-btn-]").forEach(button => {
        button.addEventListener("click", function () {
            let postId = this.id.replace("toggle-btn-", "");
            let limitedComments = document.getElementById("limited-comments-" + postId);
            let fullComments = document.getElementById("full-comments-" + postId);
            let toggleBtn = this;

            if (fullComments.style.display === "none") {
                fullComments.style.display = "block";
                limitedComments.style.display = "none";
                toggleBtn.textContent = "Hide comments";
            } else {
                fullComments.style.display = "none";
                limitedComments.style.display = "block";
                toggleBtn.textContent = "View all comments";
            }
        });
    });
});
