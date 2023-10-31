const express = require('express');
const jwt = require('jsonwebtoken');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const path = require('path');
const bcrypt = require('bcryptjs');
const rateLimit = require('express-rate-limit');
const visit = require('./bot')

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 20, // limit each IP to 10 requests per windowMs
  message: 'Too many requests from this IP, please try again later',
  standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers
});


const app = express();
app.enable('trust proxy');
app.use(bodyParser.json());

const { MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB, SECRET_KEY } = process.env;

mongoose.connect(`mongodb://mongo:27017/${MONGO_DB}`, { 
    useNewUrlParser: true, 
    useUnifiedTopology: true, 
    authSource: "admin",
    user: MONGO_USERNAME,
    pass: MONGO_PASSWORD
 });
const db = mongoose.connection;

db.on('error', (error) => console.error('MongoDB connection error:', error));
db.once('open', () => console.log('Connected to MongoDB'));

const userSchema = new mongoose.Schema({
    username: String,
    password: String,
    emailNotifications: Boolean,
    profileVisibility: String,
    userTheme: String,
    blockedUsers: [mongoose.Types.ObjectId],
    friends: [mongoose.Types.ObjectId],
    sentFriendRequests: [mongoose.Types.ObjectId],
    receivedFriendRequests: [mongoose.Types.ObjectId]

});


const User = mongoose.model('User', userSchema);

const postSchema = new mongoose.Schema({
    userId: mongoose.Types.ObjectId,
    content: String
});

const Post = mongoose.model('Post', postSchema);
const messageSchema = new mongoose.Schema({
    senderId: mongoose.Types.ObjectId,
    receiverId: mongoose.Types.ObjectId,
    content: String,
    timestamp: { type: Date, default: Date.now },
    groupId: mongoose.Types.ObjectId
});

const Message = mongoose.model('Message', messageSchema);



const groupSchema = new mongoose.Schema({
    name: String,
    members: [mongoose.Types.ObjectId]
});

const Group = mongoose.model('Group', groupSchema);

const verifyToken = (req, res, next) => {
    const token = req.headers['authorization'];
  
    if (!token) {
      return res.status(403).json({ error: 'Token is not provided' });
    }
  
    jwt.verify(token, SECRET_KEY, (err, decoded) => {
      if (err) {
        return res.status(401).json({ error: 'Invalid token' });
      }
  
      req.userId = decoded.userId;
      next();
    });
  };

  function sendResponse(res, status, data, requestType) {
    res.status(200).json({ status, data: { ...data, requestType } });
  }
  

  app.post('/register', async (req, res) => {
    const { username, password } = req.body;
  
    try {
      const existingUser = await User.findOne({ username });
  
      if (existingUser) {
        sendResponse(res, 'ERROR', { error: "User already exist" }, 'register');
        return;
      }
  
      const hashedPassword = await bcrypt.hash(password, 10);
  
      const user = new User({ username, password: hashedPassword });
      await user.save();
  
      sendResponse(res, 'SUCCESS', { message: 'Registration successful' }, 'register');
    } catch (error) {
      sendResponse(res, 'ERROR', { error: error.message }, 'register');
    }
  });

app.post('/login', async (req, res) => {
    const { username, password } = req.body;
  
    try {
      const user = await User.findOne({ username });
  
      if (!user) {
        sendResponse(res, 'ERROR', { error: 'Invalid credentials' }, 'login');
        return;
      }
  
      const isPasswordValid = await bcrypt.compare(password, user.password);
  
      if (!isPasswordValid) {
        sendResponse(res, 'ERROR', { error: 'Invalid credentials' }, 'login');
        return;
      }
  
      const token = jwt.sign({ userId: user._id }, SECRET_KEY, { expiresIn: '24h' });
  
      sendResponse(res, 'SUCCESS', { token }, 'login');
    } catch (error) {
        sendResponse(res, 'ERROR', { error: 'Invalid credentials' }, 'login');
    }
  });

app.get('/posts/',verifyToken, async (req, res) => {
    const userId = req.userId;
    try {
        const posts = await Post.find({ userId });
        sendResponse(res, 'SUCCESS', { posts }, 'postsGet');
    } catch (error) {
        sendResponse(res, 'ERROR', { error: error.message }, 'postsGet');
    }
});

app.post('/posts',verifyToken, async (req, res) => {
    const { content } = req.body;
    const userId = req.userId;
    try {
        const post = new Post({ userId, content });
        await post.save();
        sendResponse(res, 'SUCCESS', { message: "Post created succefull" }, 'postsAdd');
    } catch (error) {
        sendResponse(res, 'ERROR', { error: error.message }, 'postsAdd');
    }
});

app.post('/sendFriendRequest', verifyToken, async (req, res) => {
    const { friendUsername } = req.body;
  
    try {
        const user = await User.findById(req.userId);
        if (!user) {
            sendResponse(res, 'ERROR', { error: 'User not found' }, 'friendRequest');
            return;
        }
  
        const friend = await User.findOne({ username: friendUsername });
        if (!friend) {
            sendResponse(res, 'ERROR', { error: 'Friend not found' }, 'friendRequest');
            return;
        }
  
        if (user.friends.includes(friend._id)) {
            sendResponse(res, 'ERROR', { error: 'You are already friends with this user' }, 'friendRequest');
            return;
        }
  
        user.friends.push(friend._id);  
        await user.save();
  
        sendResponse(res, 'SUCCESS', { message: 'Friend request sent successfully' }, 'friendRequest');
    } catch (error) {
        sendResponse(res, 'ERROR', { error: error.message }, 'friendRequest');
    }
});


  app.post('/blockUser', verifyToken, async (req, res) => {
    const { friendUsername } = req.body;

    try {
        const user = await User.findById(req.userId);
        if (!user) {
            sendResponse(res, 'ERROR', { error: 'User not found' }, 'blockUser');
            return;
        }
        const friend = await User.findOne({ username: friendUsername });
        if (!friend) {
          sendResponse(res, 'ERROR', { error: 'Friend not found' }, 'friendRequest');
          return;
        }
        user.blockedUsers.push(friend._id);
        await user.save();

        sendResponse(res, 'SUCCESS', { message: 'User blocked successfully' }, 'blockUser');
    } catch (error) {
        sendResponse(res, 'ERROR', { error: error.message }, 'blockUser');
    }
});

app.post('/unblockUser', verifyToken, async (req, res) => {
    const { friendUsername } = req.body;

    try {
        const user = await User.findById(req.userId);
        if (!user) {
            sendResponse(res, 'ERROR', { error: 'User not found' }, 'unblockUser');
            return;
        }
        const friend = await User.findOne({ username: friendUsername });
        if (!friend) {
          sendResponse(res, 'ERROR', { error: 'Friend not found' }, 'friendRequest');
          return;
        }
        user.blockedUsers = user.blockedUsers.filter(id => id !== friend._id);
        await user.save();

        sendResponse(res, 'SUCCESS', { message: 'User unblocked successfully' }, 'unblockUser');
    } catch (error) {
        sendResponse(res, 'ERROR', { error: error.message }, 'unblockUser');
    }
});

app.post('/removeFriend', verifyToken, async (req, res) => {
    const { friendUsername } = req.body;

    try {
        const user = await User.findById(req.userId);
        if (!user) {
            sendResponse(res, 'ERROR', { error: 'User not found' }, 'removeFriend');
            return;
        }
        const friend = await User.findOne({ username: friendUsername });
        if (!friend) {
          sendResponse(res, 'ERROR', { error: 'Friend not found' }, 'removeFriend');
          return;
        }
        user.friends = user.friends.filter(id => {friend._id,id.toString() != friend._id.toString()});
        await user.save();
        sendResponse(res, 'SUCCESS', { message: 'Friend removed successfully' }, 'removeFriend');
    } catch (error) {
        sendResponse(res, 'ERROR', { error: error.message }, 'removeFriend');
    }
});
app.get('/getFriends', verifyToken, async (req, res) => {
    try {
        const user = await User.findById(req.userId);
        let friends = []
        for(const friendId of user.friends){
            let friend = await User.findOne({_id: friendId});
            if(friend)
                friends.push(friend.username)
        }

        sendResponse(res, 'SUCCESS', { friends: friends }, 'getFriends');
    } catch (error) {
        sendResponse(res, 'ERROR', { error: error.message }, 'getFriends');
    }
});

  app.post('/settings', verifyToken, async (req, res) => {
    const { emailNotifications, profileVisibility, userTheme } = req.body;
  
    try {
      const user = await User.findById(req.userId);
      if (!user) {
        sendResponse(res, 'ERROR', { error: 'User not found' }, 'settings');
        return;
      }
  
      user.emailNotifications = emailNotifications;
      user.profileVisibility = profileVisibility;
      user.userTheme = userTheme;
  
      await user.save();
  
      sendResponse(res, 'SUCCESS', { message: 'Settings updated successfully' }, 'settings');
    } catch (error) {
      sendResponse(res, 'ERROR', { error: error.message }, 'settings');
    }
})

app.get('/settings', verifyToken, async (req, res) => {
    try {
      const user = await User.findById(req.userId);
      if (!user) {
        sendResponse(res, 'ERROR', { error: 'User not found' }, 'settings');
        return;
      }
  
      const userSettings = {
        emailNotifications: user.emailNotifications,
        profileVisibility: user.profileVisibility,
        userTheme: user.userTheme,
      };
  
      sendResponse(res, 'SUCCESS', { settings: userSettings }, 'settings');
    } catch (error) {
      sendResponse(res, 'ERROR', { error: error.message }, 'settings');
    }
  });

  app.post('/sendMessage', verifyToken, async (req, res) => {
    const { receiverId, content } = req.body;

    try {
        const user = await User.findById(req.userId);
        if (!user) {
            sendResponse(res, 'ERROR', { error: 'User not found' }, 'sendMessage');
            return;
        }

        const receiver = await User.findById(receiverId);
        if (!receiver) {
            sendResponse(res, 'ERROR', { error: 'Receiver not found' }, 'sendMessage');
            return;
        }

        const message = new Message({ senderId: user._id, receiverId, content });
        await message.save();

        sendResponse(res, 'SUCCESS', { message: 'Message sent successfully' }, 'sendMessage');
    } catch (error) {
        sendResponse(res, 'ERROR', { error: error.message }, 'sendMessage');
    }
});

app.get('/messages/:userId', verifyToken, async (req, res) => {
    const { userId } = req.params;

    try {
        const user = await User.findById(req.userId);
        if (!user) {
            sendResponse(res, 'ERROR', { error: 'User not found' }, 'getMessages');
            return;
        }

        const messages = await Message.find({
            $or: [
                { senderId: user._id, receiverId: mongoose.Types.ObjectId(userId) },
                { senderId: mongoose.Types.ObjectId(userId), receiverId: user._id }
            ]
        }).sort({ timestamp: 1 });

        sendResponse(res, 'SUCCESS', { messages }, 'getMessages');
    } catch (error) {
        sendResponse(res, 'ERROR', { error: error.message }, 'getMessages');
    }
});

app.post('/createGroup', verifyToken, async (req, res) => {
    const { groupName, members } = req.body;

    try {
        const user = await User.findById(req.userId);
        if (!user) {
            sendResponse(res, 'ERROR', { error: 'User not found' }, 'createGroup');
            return;
        }
        let memberIds = []
        for(const member of members){
            const memberObject = await User.findOne({ username: member });
            if(memberObject)
                memberIds.push(memberObject._ids);
        }
        const group = new Group({ name: groupName, members: [...memberIds, req.userId] });
        await group.save();

        sendResponse(res, 'SUCCESS', { message: 'Group created successfully' }, 'createGroup');
    } catch (error) {
        sendResponse(res, 'ERROR', { error: error.message }, 'createGroup');
    }
});

app.get('/group/:groupId', verifyToken, async (req, res) => {
    const { groupId } = req.params;

    try {
        const group = await Group.findById(groupId);
        if (!group) {
            sendResponse(res, 'ERROR', { error: 'Group not found' }, 'getGroupInfo');
            return;
        }

        sendResponse(res, 'SUCCESS', { group }, 'getGroupInfo');
    } catch (error) {
        sendResponse(res, 'ERROR', { error: error.message }, 'getGroupInfo');
    }
});

app.post('/sendMessageToGroup', verifyToken, async (req, res) => {
    const { groupId, content } = req.body;

    try {
        const user = await User.findById(req.userId);
        if (!user) {
            sendResponse(res, 'ERROR', { error: 'User not found' }, 'sendMessageToGroup');
            return;
        }

        const group = await Group.findById(groupId);
        if (!group) {
            sendResponse(res, 'ERROR', { error: 'Group not found' }, 'sendMessageToGroup');
            return;
        }

        const message = new Message({ senderId: user._id, groupId, content });
        await message.save();

        sendResponse(res, 'SUCCESS', { message: 'Message sent to group successfully' }, 'sendMessageToGroup');
    } catch (error) {
        sendResponse(res, 'ERROR', { error: error.message }, 'sendMessageToGroup');
    }
});

app.get('/groupMessages/:groupId', verifyToken, async (req, res) => {
    const { groupId } = req.params;

    try {
        const user = await User.findById(req.userId);
        if (!user) {
            sendResponse(res, 'ERROR', { error: 'User not found' }, 'getGroupMessages');
            return;
        }

        const messages = await Message.find({ groupId }).sort({ timestamp: 1 });

        sendResponse(res, 'SUCCESS', { messages }, 'getGroupMessages');
    } catch (error) {
        sendResponse(res, 'ERROR', { error: error.message }, 'getGroupMessages');
    }
});

app.get('/report', (req, res) => {
    res.sendFile(path.join(__dirname,"report.html"));
});

app.post('/report',limiter, (req, res) => {
    const reportedLink = req.body.link;
    visit(reportedLink);
    res.send('Link reported successfully!');
});

app.post('/log', async (req, res) => {
    const { logs } = req.body;
    console.log(`[LOG]: ${logs}`);
    sendResponse(res, 'SUCCESS', {  }, 'loggerFinish');
});

app.get('/login', async (req, res) => {
    res.sendFile(path.join(__dirname,"login.html"));
});

app.get('/register', async (req, res) => {
    res.sendFile(path.join(__dirname,"register.html"));
});

app.get('/connector', async (req, res) => {
    res.sendFile(path.join(__dirname,"connector.html"));
});

app.get('/styles/styles.css', async (req, res) => {
    res.sendFile(path.join(__dirname,"styles.css"));
});

app.listen(3001, () => {
    console.log('API server is running on http://localhost:3001');
});
