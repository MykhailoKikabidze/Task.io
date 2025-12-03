import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    access_token: null,
    refresh_token: null,
    user_id: null,
    email: null,
    password: null,
    name: null,
    surname: null,
    img_url: null,
  }),
  actions: {
    setTokens(accessToken, refreshToken) {
      this.access_token = accessToken;
      this.refresh_token = refreshToken;

      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
    },
    getAccessToken() {
      return this.access_token;
    },
    getRefreshToken() {
      return this.refresh_token;
    },
    setUserInfo(email, password, name, surname, imgUrl) {
      this.email = email;
      this.password = password;
      this.name = name;
      this.surname = surname;
      this.img_url = imgUrl;

      localStorage.setItem("user", JSON.stringify({
      name: name,
      surname: surname,
      email: email,
      imgUrl: imgUrl,
      password: password,
    }));
    },
    getUserInfo() {
      return {
        email: this.email,
        password: this.password,
        name: this.name,
        surname: this.surname,
        img_url: this.img_url,
      };
    },
    setUserId(userId) {
      this.user_id = userId;
      localStorage.setItem('user_id', userId);
    },
    getUserId() {
      return this.user_id;
    },
  }
});
