document.addEventListener('DOMContentLoaded', () => {
    const postForm = document.getElementById('postForm');
    const postList = document.getElementById('postList');

    postForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const content = document.getElementById('content').value;

        try {
            await sendRequest('posts', 'POST', { content });
        } catch (error) {
            console.error('Error creating post:', error);
        }
    });

    async function loadPosts() {
        postList.innerHTML = '';

        try {
            await sendRequest('posts', 'GET');
        } catch (error) {
            console.error('Error fetching posts:', error);
        }
    }

    loadPosts();
});