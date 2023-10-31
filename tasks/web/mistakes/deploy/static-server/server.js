const express = require('express');
const path = require('path');

const app = express();

app.set('view engine', 'ejs');

app.set('views', path.join(__dirname, 'views'));

app.use(express.static(path.join(__dirname, 'static')));

app.use((req, res, next) => {
  res.locals.BASE = process.env.API_BASE;
  next();
});

app.get('/', (req, res) => {
    res.render('index');
});

app.get('/post', (req, res) => {
    res.render('post');
});

app.get('/friends', (req, res) => {
    res.render('friends');
});

app.get('/settings', (req, res) => {
    res.render('settings');
});

app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});