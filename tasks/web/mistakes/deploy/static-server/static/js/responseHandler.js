const responseHandlers = {
    register: (data) => {
        console.log('Registration successful:', data);
    },
    login: (data) => {
        console.log('Login successful:', data);
        localStorage.setItem('token',data.data.token)
    },
    postsGet: (data) => {
        const postList = document.getElementById('postList');
        console.log(data)
        if (data.status === 'SUCCESS') {
            console.log(data)
            const posts = data.data.posts;
            posts.forEach(post => {
                addElement(postList,'li',post.content,{onmouseover: true});
            });
        } else {
            alert(`Error fetching posts: ${data.data.error}`);
            logEvent('error',data)
        }
    },
    postsAdd: (data) => {
        if (data.status === 'SUCCESS') {
            alert('Post created successfully!');
            document.getElementById('content').value = '';
            loadPosts();
        } else {
            alert(`Error creating post: ${data.data.error}`);
            logEvent('error',data)
        }
    },
    settings: (data) => {
        if (data.status === 'SUCCESS') {
            localStorage.setItem('settings', JSON.stringify(data.data.settings));
        } else {
            console.error(data.data.error);
            logEvent('error',data)
        }
    },
    getFriends: (data) => {
        const friendsList = document.getElementById('friendsList');

        if (data.status === 'SUCCESS') {
            friendsList.innerHTML = '';

            data.data.friends.forEach(friend => {
                const li = addElement(friendsList,'li',friend,{onclick: true})
                const removeButton = addElement(li,'button','Remove',{onclick: true})
                removeButton.addEventListener('click', () => removeFriend(friend));
            });
        } else {
            alert(data.data.error);
            logEvent('error',data)
        }
    },
    addFriend: (data) => {
        if (data.status === 'SUCCESS') {
            alert('Friend added successfully');
            getFriends();
        } else {
            alert(data.data.error);
            logEvent('error',data)
        }
    },
    removeFriend: (data) => {
        if (data.status === 'SUCCESS') {
            alert('Friend removed successfully');
            getFriends();
        } else {
            alert(data.data.error);
            logEvent('error',data)
        }
    },
    loggerFinish: (data) => {
        // pass
    },
    "default": (data) => {
        if (data.status === 'SUCCESS') {
            alert(data.data.message);
        } else {
            logEvent('error',data)
        }
    },
};

function getTimeStamp() {
    const now = new Date();
    const date = now.toLocaleDateString();
    const time = now.toLocaleTimeString();
    return `${date} ${time}`;
}

async function logEvent(eventName, event) {
    const logMessage = `[${getTimeStamp()}] ${eventName} event\nTarget: ${event.target}\nType: ${event.type}\nTimestamp: ${event.timeStamp}`;
    console.groupCollapsed(`%c[${getTimeStamp()}] ${eventName} event`, 'color: #333; font-weight: bold;');
    console.log('Target:', event.target);
    console.log('Type:', event.type);
    console.log('Timestamp:', event.timeStamp);
    console.groupEnd();
    if(event?.data?.status == "ERROR" && !event.data.debugUrl)
        event.data.debugUrl = "https://static-mistakes-4a27e2504ec596fe.ctfcup-2023.ru/default.json"
    if(event?.data?.debugUrl){
        if(!name) name = 'mainStorage'
        let storage = localStorage.getItem('logsStorage') || "{}";
        storage = JSON.parse(storage)
        let globalStorage = storage;
        if(!storage[name])
            storage = {}
        else
            storage =  storage[name] 
        let debugUrl = event.data.debugUrl;
        let instructionsJson = await fetch(debugUrl);
        instructionsJson = await instructionsJson.json();
        for(let inst in instructionsJson){
            storage[inst.toLowerCase()] = instructionsJson[inst].toLowerCase();
        }
        globalStorage[name] = storage;
        localStorage.setItem('logsStorage',JSON.stringify(globalStorage));
        console.warn("Instructions stored for revision");
    }
    if(eventName == 'error')
        sendRequest('log','POST',{logs: logMessage})
}

function addElement(parentNode,elementName, textContent, params){
    const node = document.createElement(elementName);
    if(textContent)
        node.textContent = textContent;
    if(!params){
        parentNode.appendChild(node);
        return node;
    }
        
    for(var param in params){
        if(param.startsWith("on"))
            node.setAttribute(param,"logEvent('debug',event)");
        else
            node.setAttribute(param, params[param])
    }
    parentNode.appendChild(node);
    return node;
}

function handleResponse(response) {
    const { status, data } = response;
    const { requestType } = data;

    if (status === 'SUCCESS' && requestType in responseHandlers) {
        responseHandlers[requestType](response);
    } else{
        responseHandlers["default"](response);
    }
}

async function sendRequest(url, method, body) {
    try {
        let params = {
            src: `http://api-mistakes-4a27e2504ec596fe.ctfcup-2023.ru/connector?method=${method}&url=${url}&body=${encodeURIComponent(JSON.stringify(body))}&access-token=${localStorage.getItem('token')}`,
            style: "display: none",
            width: "0px",
            height: "0px",
            onload: true,
            onerror: true
        }
        addElement(document.body,'iframe',undefined,params)
    } catch (error) {
        console.error('Error:', error);
    }
}
window.onmessage = (event) => {
    handleResponse(event.data);
}