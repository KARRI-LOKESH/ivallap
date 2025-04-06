document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".like-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.stopPropagation(); // Prevent event conflict
            let postId = this.dataset.postId;
            let likeCountSpan = document.getElementById(`like-count-${postId}`);

            fetch(`/like/${postId}/`, {
                method: "GET",
                headers: { "X-Requested-With": "XMLHttpRequest" },
                credentials: "same-origin",
            })
            .then(response => response.json())
            .then(data => {
                this.innerHTML = data.liked ? "👎UnLike" : "👍Like";
                likeCountSpan.textContent = data.total_likes;
            })
            .catch(error => console.error("Error:", error));
        });
    });

    // Share Button Function
    document.querySelectorAll(".share-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.stopPropagation(); // Prevent event conflict
            let postUrl = this.dataset.postUrl;
            navigator.clipboard.writeText(postUrl).then(() => {
                alert("Post link copied!");
            }).catch(err => {
                console.error("Failed to copy:", err);
            });
        });
    });

    // Double Tap (Like Post) & Single Tap (Open Post)
    document.querySelectorAll(".post").forEach(post => {
        let lastTap = 0;
        let postId = post.dataset.postId;

        post.addEventListener("pointerdown", function (event) {
            if (event.target.tagName === "BUTTON") return; // Prevent conflicts with buttons

            let currentTime = new Date().getTime();
            let tapLength = currentTime - lastTap;

            if (tapLength < 300 && tapLength > 0) { // Double Tap Detected
                likePost(postId);
            } else {
                setTimeout(() => {
                    if (new Date().getTime() - lastTap >= 300) { // Single Tap
                        window.location.href = `/posts/${postId}/`;
                    }
                }, 300);
            }

            lastTap = currentTime;
        });
    });

    function likePost(postId) {
        fetch(`/like/${postId}/`, {
            method: "GET",
            headers: { "X-Requested-With": "XMLHttpRequest" },
            credentials: "same-origin",
        })
        .then(response => response.json())
        .then(data => {
            let likeCountSpan = document.getElementById(`like-count-${postId}`);
            likeCountSpan.textContent = data.total_likes;

            let likeButton = document.querySelector(`.like-btn[data-post-id="${postId}"]`);
            if (likeButton) {
                likeButton.innerHTML = data.liked ? "👎UnLike" : "👍Like";
            }
        })
        .catch(error => console.error("Error:", error));
    }
});
