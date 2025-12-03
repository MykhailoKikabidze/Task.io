<template>
    <v-container class="profile-container">
        <v-card class="pa-6" elevation="8" rounded="lg" width="420">

            <div class="header-section">
                <div class="avatar-container">
                    <v-avatar size="100" class="avatar">
                        <v-img :src="user.avatar || placeholderAvatar" />
                    </v-avatar>
                    <v-btn icon class="avatar-btn" @click="triggerFileInput">
                        <v-icon icon="mdi-camera"></v-icon>
                    </v-btn>
                    <input ref="fileInput" type="file" accept="image/png, image/jpeg" class="d-none"
                        @change="onAvatarSelected" />
                </div>
                <div class="user-info">
                    <div class="username">{{ fullName }}</div>
                </div>

                <v-btn icon v-bind="props" @click="router.back()" class="close-btn">
                    <v-icon icon="mdi-close"></v-icon>
                </v-btn>
            </div>

            <v-divider class="my-3"></v-divider>

            <h4 class="section-title">PERSONAL DETAILS</h4>

            <v-text-field v-model="firstName" placeholder="First Name" prepend-inner-icon="mdi-account"
                :error-messages="firstNameError" @input="validateFirstName" variant="outlined"
                density="compact"></v-text-field>

            <v-text-field v-model="lastName" placeholder="Last Name" prepend-inner-icon="mdi-account" variant="outlined"
                :error-messages="lastNameError" @input="validateLastName" density="compact"></v-text-field>

            <v-text-field v-model="user.email" placeholder="Email Address" prepend-inner-icon="mdi-email-outline"
                variant="outlined" density="compact" disabled></v-text-field>

            <v-text-field v-model="passwordDefined" placeholder="Password" append-inner-icon="mdi-pencil"
                prepend-inner-icon="mdi-lock-outline" variant="outlined" density="compact" type="password"
                @click:append-inner="togglePasswordChange"></v-text-field>

            <div v-if="showPasswordChange">
                <v-text-field v-model="currentPassword" placeholder="Current Password" variant="outlined"
                    :error-messages="currentPasswordError" @input="validateCurrentPassword" density="compact"
                    type="password"></v-text-field>

                <v-text-field v-model="newPassword" placeholder="New Password" :error-messages="newPasswordError"
                    @input="validateNewPassword" variant="outlined" density="compact" type="password"></v-text-field>

                <v-text-field v-model="confirmPassword" placeholder="Confirm New Password"
                    :error-messages="confirmPasswordError" @input="validateConfirmPassword" variant="outlined"
                    density="compact" type="password"></v-text-field>
            </div>

            <v-tooltip text="Save changes" location="bottom">
                <template v-slot:activator="{ props }">
                    <v-btn icon v-bind="props" class="bot-btn" @click="saveProfile">
                        <v-icon icon="mdi-check"></v-icon>
                    </v-btn>
                </template>
            </v-tooltip>

            <v-tooltip text="Logout" location="bottom">
                <template v-slot:activator="{ props }">
                    <v-btn icon v-bind="props" class="bot-btn" @click="logout">
                        <v-icon icon="mdi-logout"></v-icon>
                    </v-btn>
                </template>
            </v-tooltip>

            <v-tooltip text="Delete account" location="bottom">
                <template v-slot:activator="{ props }">
                    <v-btn icon v-bind="props" class="bot-btn" @click="confirmDelete = true">
                        <v-icon icon="mdi-delete"></v-icon>
                    </v-btn>
                </template>
            </v-tooltip>

            <v-snackbar v-model="snackbarErrVisible" color="red" timeout="3000">
                <div class="text-center">
                    {{ snackbarErrMessage }}
                </div>
            </v-snackbar>
            <v-snackbar v-model="snackbarDoneVisible" color="green" timeout="3000">
                <div class="text-center">
                    {{ snackbarDoneMessage }}
                </div>
            </v-snackbar>
        </v-card>

        <v-dialog v-model="confirmDelete" max-width="400">
            <v-card class="pa-4" shaped>
                <v-card-title class="text-h6">Delete account?</v-card-title>
                <v-card-text>
                    This action is irreversible. Are you sure you want to delete your account?
                </v-card-text>
                <v-card-actions>
                    <v-spacer />
                    <v-btn text @click="confirmDelete = false">Cancel</v-btn>
                    <v-btn color="red darken-1" @click="deleteAccount">Delete</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-container>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { authFetch } from '@/utils/authFetch';

const router = useRouter();
const auth = useAuthStore();

const snackbarErrMessage = ref('');
const snackbarErrVisible = ref(false);
const snackbarDoneMessage = ref('');
const snackbarDoneVisible = ref(false);

const confirmDelete = ref(false);

const placeholderAvatar = ref("/src/assets/avatar.jpg");
const isDirtyAvatar = ref(false);
const avatarFile = ref(null);
let firstName = ref("");
let lastName = ref("");

const fullName = computed(() => `${user.value.name} ${user.value.surname}`);

const firstNameError = ref("");
const lastNameError = ref("");

let passwordDefined = ref("");

const user = ref({
    name: '',
    surname: '',
    email: '',
    password: '',
    avatar: '',
});

onMounted(() => {
    const { name, surname, email, password, img_url } = auth.getUserInfo();

    if (!name || !surname || !email || !password || !img_url) {
        const userLocal = JSON.parse(localStorage.getItem("user"))

        user.value.name = userLocal.name;
        user.value.surname = userLocal.surname;
        user.value.password = userLocal.password;
        user.value.email = userLocal.email;
        user.value.avatar = userLocal.imgUrl;

        firstName.value = userLocal.name || '';
        lastName.value = userLocal.surname || '';
        passwordDefined = userLocal.password;

        auth.setUserInfo(userLocal.email, userLocal.password, userLocal.name, userLocal.surname, userLocal.imgUrl);
    }
    else {
        user.value.name = name;
        user.value.surname = surname;
        user.value.password = password;
        user.value.email = email;
        user.value.avatar = img_url;

        firstName.value = name || '';
        lastName.value = surname || '';
        passwordDefined = password;
    }
});


const showPasswordChange = ref(false);
const currentPassword = ref("");
const newPassword = ref("");
const confirmPassword = ref("");

const currentPasswordError = ref("");
const newPasswordError = ref("");
const confirmPasswordError = ref("");

const validateFirstName = () => {
    if (firstName.value == '') {
        firstNameError.value = '';
        return;
    }

    const nameRegex = /^[A-Z][a-z]+$/;
    firstNameError.value = nameRegex.test(firstName.value) ? '' : 'First name must start with a capital letter and contain only letters';
};

const validateLastName = () => {
    if (lastName.value == '') {
        lastNameError.value = '';
        return;
    }

    const nameRegex = /^[A-Z][a-z]+$/;
    lastNameError.value = nameRegex.test(lastName.value) ? '' : 'Last name must start with a capital letter and contain only letters';
};

const validateNewPassword = () => {
    const passwordRegex = /^.*(?=.{8,})(?=.*[a-zA-Z])(?=.*\d)(?=.*[!#$%&? "]).*$/;

    if (newPassword.value == '') {
        newPasswordError.value = '';
        return;
    }

    newPasswordError.value = passwordRegex.test(newPassword.value)
        ? ''
        : 'Password must be at least 8 characters long, include a number, a letter, and a special character';
};

const validateCurrentPassword = () => {
    if (currentPassword.value == '') {
        currentPasswordError.value = '';
        return;
    }
    currentPasswordError.value = currentPassword.value === user.value.password ? '' : 'Incorrect current password';
};

const validateConfirmPassword = () => {
    if (confirmPassword.value == '') {
        confirmPasswordError.value = '';
        return;
    }
    confirmPasswordError.value = confirmPassword.value === newPassword.value ? '' : 'Passwords do not match';
};

const fileInput = ref(null);
const triggerFileInput = () => fileInput.value.click();
const onAvatarSelected = e => {
    const file = e.target.files[0];
    if (!file) return;
    if (!file.type.startsWith("image/jpeg") && !file.type.startsWith("image/png")) {
        snackbarErrMessage.value = "Please select a valid image file (JPEG or PNG)";
        snackbarErrVisible.value = true;
        setTimeout(() => {
            snackbarErrVisible.value = false;
            snackbarErrMessage.value = '';
        }, 3000);
        console.error("Not an image!");
        return;
    }
    const reader = new FileReader();
    reader.onload = evt => {
        user.value.avatar = evt.target.result;
        isDirtyAvatar.value = true;
        avatarFile.value = file;
    };
    reader.readAsDataURL(file);
};

const togglePasswordChange = () => {
    showPasswordChange.value = !showPasswordChange.value;
    if (!showPasswordChange.value) {
        currentPassword.value = "";
        newPassword.value = "";
        confirmPassword.value = "";

        currentPasswordError.value = "";
        newPasswordError.value = "";
        confirmPasswordError.value = "";
    }
};

const saveProfile = async () => {
    let validForm = firstNameError.value === '' &&
        lastNameError.value === '';

    if (firstName.value === '' || lastName.value === '') {
        firstNameError.value = firstName.value === '' ? 'First name is required' : '';
        lastNameError.value = lastName.value === '' ? 'Last name is required' : '';
        validForm = false;
    }

    if (showPasswordChange.value) {
        validForm = validForm &&
            currentPasswordError.value === '' &&
            newPasswordError.value === '' &&
            confirmPasswordError.value === '';

        if (currentPassword.value === '' || newPassword.value === '' || confirmPassword.value === '') {
            currentPasswordError.value = currentPassword.value === '' ? 'Current password is required' : '';
            newPasswordError.value = newPassword.value === '' ? 'New password is required' : '';
            confirmPasswordError.value = confirmPassword.value === '' ? 'Confirm password is required' : '';
            validForm = false;
        }
    }

    if (!validForm) {
        console.warn("Form is invalid, cannot save profile");
        return;
    }

    const token = auth.getAccessToken();

    try {
        const payload = {
            name: firstName.value,
            surname: lastName.value,
        };
        if (showPasswordChange.value) {
            payload.password = newPassword.value;
        }
        else {
            payload.password = user.value.password;
        }

        const resInfo = await authFetch('/api/v1/auth/me', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });
        if (!resInfo.ok) throw new Error('Failed updating profile');

        if (isDirtyAvatar.value && avatarFile.value) {
            const form = new FormData();
            form.append('file', avatarFile.value);
            const resImg = await fetch('http://localhost:8000/api/v1/auth/me/img', {
                method: 'PATCH',
                headers: { Authorization: `Bearer ${token}` },
                body: form
            });
            if (!resImg.ok) throw new Error('Failed uploading avatar');
        }

        const meRes = await fetch('http://localhost:8000/api/v1/auth/me', {
            headers: { Authorization: `Bearer ${token}` }
        });
        if (meRes.ok) {
            const info = await meRes.json();
            if (showPasswordChange.value) {
                auth.setUserInfo(info.email, newPassword, info.name, info.surname, info.img_url);
                localStorage.setItem("user", JSON.stringify({
                    name: info.name,
                    surname: info.surname,
                    email: info.email,
                    imgUrl: info.img_url,
                    password: newPassword,
                }));
            } else {
                auth.setUserInfo(info.email, user.value.password, info.name, info.surname, info.img_url);
                localStorage.setItem("user", JSON.stringify({
                    name: info.name,
                    surname: info.surname,
                    email: info.email,
                    imgUrl: info.img_url,
                    password: user.value.password,
                }));
            }

            firstName.value = info.name;
            lastName.value = info.surname;
        }

        snackbarDoneVisible.value = true;
        snackbarDoneMessage.value = 'Profile updated!';
        isDirtyAvatar.value = false;
        showPasswordChange.value = false;
        setTimeout(() => {
            snackbarDoneVisible.value = false;
            snackbarDoneMessage.value = '';
        }, 3000);
    } catch (err) {
        console.error(err);
        snackbarErrVisible.value = true;
        snackbarErrMessage.value = 'Error saving profile';
        setTimeout(() => {
            snackbarErrVisible.value = false;
            snackbarErrMessage.value = '';
        }, 3000);
    }
};

async function logout() {
    try {
        await fetch('http://localhost:8000/api/v1/auth/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${auth.access_token}`,
            },
            credentials: 'include'
        });
    } catch (e) {
        console.warn('Logout request failed, but proceeding anyway');
    }

    auth.setTokens(null, null);
    auth.setUserInfo(null, null, null, null);
    auth.setUserId(null);

    localStorage.removeItem("user");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    router.push('/loginpage');
}

async function deleteAccount() {
    try {
        const response = await authFetch('/api/v1/auth/me', {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${auth.getAccessToken()}`,
            },
            credentials: 'include'
        });

        const message = await response.json();

        if (!response.ok) {
            throw new Error(message.detail || 'Failed to delete account');
        }
        confirmDelete.value = false;
        auth.setTokens(null, null);
        auth.setUserInfo(null, null, null, null);
        auth.setUserId(null);
        localStorage.removeItem("user");
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        router.push('/loginpage');
    } catch (err) {
        console.error('Error while delete account: ', err);
    }
}
</script>

<style scoped>
.profile-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}

.header-section {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 16px;
}

.avatar-container {
    position: relative;
    display: flex;
    align-items: center;
}

.avatar {
    cursor: pointer;
    transition: box-shadow 0.3s;
}

.avatar-btn {
    position: absolute;
    right: -10px;
    top: 65px;
    background-color: #1e88e5;
    color: #fff;
    max-width: 35px;
    max-height: 35px;
    border-radius: 50%;
    box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
}

.avatar-btn .v-icon {
    font-size: 18px;
}

.close-btn {
    position: absolute;
    right: 10px;
    top: 10px;
    color: #fff;
    max-width: 35px;
    max-height: 35px;
    background-color: transparent !important;
    box-shadow: none !important;
}

.bot-btn {
    color: #fff;
    margin-top: 10px;
    margin-left: 55px;
    background-color: transparent !important;
    box-shadow: none !important;
}

.user-info {
    flex-grow: 1;
    text-align: left;
    margin-left: 30px;
}

.username {
    font-weight: bold;
    font-size: 18px;
}

.section-title {
    font-size: 14px;
    color: #888;
    margin-bottom: 8px;
    text-transform: uppercase;
}

.mt-2 {
    margin-top: 16px;
}

.mt-3 {
    margin-top: 24px;
}
</style>
