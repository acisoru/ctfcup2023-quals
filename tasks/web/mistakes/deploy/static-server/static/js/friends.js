async function sendFriendRequest(friendUsername) {
    const body = { friendUsername };
    await sendRequest('sendFriendRequest', 'POST', body);
}

async function acceptFriendRequest(friendUsername) {
    const body = { friendUsername };
    await sendRequest('acceptFriendRequest', 'POST', body);
}

async function blockUser(friendUsername) {
    const body = { friendUsername };
    await sendRequest('blockUser', 'POST', body);
}

async function unblockUser(friendUsername) {
    const body = { friendUsername };
    await sendRequest('unblockUser', 'POST', body);
}

async function removeFriend(friendUsername) {
    const body = { friendUsername };
    await sendRequest('removeFriend', 'POST', body);
}

async function getFriends() {
    await sendRequest('getFriends', 'GET', undefined);
}
