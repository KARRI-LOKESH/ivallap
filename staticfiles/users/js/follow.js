document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.follow-toggle-btn').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();  // Prevent form submission

            const form = button.closest('form');
            const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;  // Get CSRF token
            const userId = form.action.split('/').slice(-2, -1)[0];  // Extract user ID from the form action URL

            const url = form.action;  // Get the form action URL (the follow/unfollow endpoint)

            // Optimistically toggle the button text
            const currentAction = button.textContent.trim();

            if (currentAction === 'Follow') {
                button.textContent = 'Unfollow';  // Change text to Unfollow immediately
                button.classList.remove('btn-follow');
                button.classList.add('btn-unfollow');
            } else {
                button.textContent = 'Follow';  // Change text to Follow immediately
                button.classList.remove('btn-unfollow');
                button.classList.add('btn-follow');
            }

            // Send AJAX request to the backend to toggle follow/unfollow
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(res => {
                if (res.status === 204) {
                    // Successful response, no action needed here since we updated the button already
                } else {
                    // In case of an error, revert the button text and classes
                    if (currentAction === 'Unfollow') {
                        button.textContent = 'Follow';
                        button.classList.remove('btn-unfollow');
                        button.classList.add('btn-follow');
                    } else {
                        button.textContent = 'Unfollow';
                        button.classList.remove('btn-follow');
                        button.classList.add('btn-unfollow');
                    }
                }
            })
            .catch(error => {
                console.error('Error toggling follow:', error);
                // In case of network error, revert the button text and classes
                if (currentAction === 'Unfollow') {
                    button.textContent = 'Follow';
                    button.classList.remove('btn-unfollow');
                    button.classList.add('btn-follow');
                } else {
                    button.textContent = 'Unfollow';
                    button.classList.remove('btn-follow');
                    button.classList.add('btn-unfollow');
                }
            });
        });
    });
});
document.addEventListener('DOMContentLoaded', () => {
    const followForm = document.getElementById('followForm');
    const followButton = document.getElementById('followButton');
    const countSpan = document.getElementById('followers-count');

    if (followForm && followButton) {
        followButton.addEventListener('click', function (e) {
            e.preventDefault();

            fetch(followForm.action, {
                method: "POST",
                headers: {
                    "X-CSRFToken": followForm.querySelector('[name=csrfmiddlewaretoken]').value,
                    "X-Requested-With": "XMLHttpRequest"
                },
            })
            .then(res => {
                if (res.status === 204) {
                    // Toggle button text
                    const isNowFollowing = followButton.textContent.trim() === "Follow";
                    followButton.textContent = isNowFollowing ? "Unfollow" : "Follow";

                    // Update count
                    if (countSpan) {
                        let current = parseInt(countSpan.textContent);
                        countSpan.textContent = isNowFollowing ? current + 1 : current - 1;
                    }
                }
            })
            .catch(err => console.error("Follow error:", err));
        });
    }
});
