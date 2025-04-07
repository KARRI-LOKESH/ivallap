document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".like-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.stopPropagation();
            let postId = this.dataset.postId;
            likePost(postId);
        });
    });

    // Share Button Function
    document.querySelectorAll(".share-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.stopPropagation();
            let postUrl = this.dataset.postUrl;
            navigator.clipboard.writeText(postUrl)
                .then(() => alert("Post link copied!"))
                .catch(err => console.error("Failed to copy:", err));
        });
    });

    // Double Tap & Double Click Like Feature
    document.querySelectorAll(".post").forEach(post => {
        let lastTap = 0;
        let postId = post.dataset.postId;

        // Double Click for Desktop
        post.addEventListener("dblclick", function (event) {
            if (!isInteractiveElement(event.target)) {
                likePost(postId);
            }
        });

        // Double Tap for Mobile
        post.addEventListener("touchend", function (event) {
            if (!isInteractiveElement(event.target)) {
                let currentTime = new Date().getTime();
                let tapLength = currentTime - lastTap;

                if (tapLength < 300 && tapLength > 0) {
                    likePost(postId);
                    lastTap = 0; // Reset to avoid multiple triggers
                } else {
                    lastTap = currentTime;
                }
            }
        });
    });

    function likePost(postId) {
        fetch(`/posts/like/${postId}/`, {  // Ensure the correct URL format
            method: "POST",  // Using POST instead of GET for better API practice
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(), // CSRF token for security
            },
            credentials: "same-origin",
        })
        .then(response => response.json())
        .then(data => {
            let likeCountSpan = document.getElementById(`like-count-${postId}`);
            if (likeCountSpan) {
                likeCountSpan.textContent = data.total_likes;
            }

            let likeButton = document.querySelector(`.like-btn[data-post-id="${postId}"]`);
            if (likeButton) {
                likeButton.innerHTML = data.liked ? "👎UnLike" : "👍Like";
            }
        })
        .catch(error => console.error("Error:", error));
    }

    function isInteractiveElement(element) {
        return element.closest("button, a, input, textarea");
    }

    function getCSRFToken() {
        let cookieValue = null;
        let cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.startsWith("csrftoken=")) {
                cookieValue = cookie.substring("csrftoken=".length, cookie.length);
                break;
            }
        }
        return cookieValue;
    }
});
