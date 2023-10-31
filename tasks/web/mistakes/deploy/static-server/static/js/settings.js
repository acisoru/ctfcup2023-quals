function initForm(){
    document.getElementById('settingsForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const userTheme = document.getElementById('userTheme').value;
        const emailNotifications = document.getElementById('emailNotifications').checked;
        const profileVisibility = document.getElementById('profileVisibility').value;
        sendRequest("settings","POST",{userTheme,emailNotifications,profileVisibility })
    });
}
sendRequest("settings","GET",undefined);