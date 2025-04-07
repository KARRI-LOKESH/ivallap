document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".like-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.stopPropagation();
            let postId = this.dataset.postId;
            likePost(postId);
        });
    });

    document.querySelectorAll(".post").forEach(post => {
        let lastTap = 0;
        let timeout;
        let postId = post.dataset.postId;

        // Double Click for Desktop
        post.addEventListener("dblclick", function (event) {
            if (!isInteractiveElement(event.target)) {
                likePost(postId);
            }
        });

        // **Improved Double Tap for Mobile**
        post.addEventListener("touchend", function (event) {
            if (!isInteractiveElement(event.target)) {
                let currentTime = new Date().getTime();
                let tapLength = currentTime - lastTap;

                if (tapLength < 300 && tapLength > 0) {
                    clearTimeout(timeout); // Clear single tap timeout
                    likePost(postId);
                    lastTap = 0;
                } else {
                    lastTap = currentTime;
                    timeout = setTimeout(() => {
                        lastTap = 0;
                    }, 300); // Reset if no second tap happens
                }
            }
        });
    });

    function likePost(postId) {
        fetch(`/posts/like/${postId}/`, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
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
                likeButton.innerHTML = data.liked ? "👎 UnLike" : "👍 Like";
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
