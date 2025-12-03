import { defineStore } from 'pinia';

export const useProjectStore = defineStore('project', {
    state: () => ({
        id: null,
        name: null,
        description: null,
        color: null,
        img_url: null,
        type: null,
        role: null
    }),
    actions: {
        setProjectInfo(id, name, description, color, img_url, type) {
            this.id = id;
            this.name = name;
            this.description = description;
            this.color = color;
            this.img_url = img_url;
            this.type = type;
        },
        getProjectInfo() {
            return {
                id: this.id,
                name: this.name,
                description: this.description,
                color: this.color,
                img_url: this.img_url,
                type: this.type
            };
        },
        setRole(role) {
            switch (role) {
                case 'owner':
                    this.role = 0;
                    break;
                case 'manager':
                    this.role = 1;
                    break;
                case 'assignee':
                    this.role = 2;
                    break;
                case 'observer':
                    this.role = 3;
                    break;
                default:
                    this.role = 3;
            }
        },
        getRole() {
            return this.role;
        }
    }
});
