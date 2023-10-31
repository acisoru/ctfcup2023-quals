#include <iostream>
#include <string>
#include <cstring>
#include <vector>
#include <map>
#include <sys/mman.h>
#include <sys/prctl.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <fcntl.h>
using namespace std;

void init() {
    struct sock_filter filter[] = {
        {0x20, 0, 0, 0x00000004},
        {0x15, 0, 12, 0xc000003e},
        {0x20, 0, 0, 0x00000000},
        {0x15, 9, 0, 0x00000000},
        {0x15, 8, 0, 0x00000001},
        {0x15, 7, 0, 0x00000002},
        {0x15, 6, 0, 0x0000003c},
        {0x15, 5, 0, 0x000000e7},
        {0x15, 4, 0, 0x0000013e},
        {0x15, 3, 0, 0x00000106},
        {0x15, 2, 0, 0x00000009},
        {0x15, 1, 0, 0x0000000c},
        {0x5, 0, 0, 0x00000001},
        {0x6, 0, 0, 0x7fff0000},
        {0x6, 0, 0, 0x00000000},
    };

    struct sock_fprog prog = {
        .len = (sizeof(filter)) / sizeof(struct sock_filter),
        filter,
    };

    prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);
    prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog);
}


struct list {
    list *next = 0;
    char *cur = 0;
    list() {}
    list(char *c) {
        cur = c;
    }
};

#define TASK_SIZE 0x20
#define MEM_BLOCK 0x120

class TaskStorage {
private:
    list *free_list = 0;
    list *used_list = 0;
    char *mem = 0;
public:
    TaskStorage() {
        mem = (char*)mmap(0, MEM_BLOCK, 7, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
        for (int i = 0; i < MEM_BLOCK; i += TASK_SIZE) {
            list *tmp = free_list;
            free_list = new list(mem+i);
            free_list->next = tmp;
        }
    }
    int add(char *task) {
        if (!free_list) return -1;
        list *tmp = used_list;
        used_list = free_list;
        free_list = free_list->next;
        used_list->next = tmp;
        strncpy(used_list->cur, task, TASK_SIZE);
        return 0;
    }
    int del(unsigned int id) {
        if (!used_list) return -1;
        if (!id) {
            list *tmp = free_list;
            free_list = used_list;
            used_list = used_list->next;
            free_list->next = tmp;
            return 0;
        }
        list *cur = used_list;
        for (int i = 0; i < id - 1; ++i) {
            if (!cur) return -1;
            cur = cur->next;
        }
        if (!cur || !cur->next) return -1;
        list *tmp = free_list;
        free_list = cur->next;
        cur->next = cur->next->next;
        free_list->next = tmp;
        return 0;
    }
    void show_all() {
        if (!used_list) {
            cout << "No tasks\n";
            return;
        }
        cout << "===========================\n";
        int id = 0;
        for (list *cur = used_list; cur; cur = cur->next, id += 1) {
            cout << id << ": " << cur->cur << '\n';
        }
        cout << "===========================\n";
    }
};

class Base {
protected:
    char type[8] = {};
public:
    char name[20] = {};
    Base() {
        cout << "Name: ";
        cin.ignore();
        cin.getline(name, 20);
    }
    void print() {
        cout << "[ " << type << "] " << name << '\n';
    }
    virtual void menu()=0;
};

class User : public Base {
private:
    TaskStorage tasks;
public:
    User() {
        strcpy(type, "user");
    }
    void menu() {
        cout << "1. Logout\n2. View my tasks\n3. Add task\n4. Delete task\n5. Edit name\n";
    }
    void add_task() {
        char task[0x20];
        cout << "Task: ";
        cin.ignore();
        cin.getline(task, 0x20);
        if (tasks.add(task) == -1) {
            cout << "No free space left\n";
            return;
        }
        cout << "Success\n";
    }
    void edit_name() {
        cout << "Current: " << name << '\n';
        cout << "New: ";
        cin.ignore();
        cin.getline(name, 0x20);
    }
    void delete_task() {
        unsigned int id;
        cout << "Id (can find if list all tasks): ";
        cin >> id;
        if (tasks.del(id) == -1) {
            cout << "Invalid id\n";
            return;
        }
        cout << "Success\n";
    }
    void show_tasks() {
        tasks.show_all();
    }
};

unsigned int cur_user_id = -1;
vector<User> users;

void logout() {
    cur_user_id = -1;
}

int read_choice() {
    cout << "> ";
    int c;
    cin >> c;
    return c;
}

int main() {
    init();
    int c;
    while (1) {
        if (cur_user_id == -1) {
            cout << "1. Login\n2. Register\n3. List all users\n> ";
            cin >> c;
            if (c == 1) {
                string name;
                cout << "Name: ";
                cin >> name;
                for (int i = 0; i < users.size(); ++i) {
                    if (users[i].name == name) {
                        cur_user_id = i;
                        break;
                    }
                }
                if (cur_user_id == -1) {
                    cout << "User not found\n";
                }
            }
            else if (c == 2) {
                users.push_back(User());
            }
            else if (c == 3) {
                if (!users.size()) {
                    cout << "No users\n";
                    continue;
                }
                cout << "===========================\n";
                for (int i = 0; i < users.size(); ++i) {
                    cout << users[i].name << '\n';
                }
                cout << "===========================\n";
            }
        }
        else {
            users[cur_user_id].menu();
            int c = read_choice();
            switch(c) {
                case 1:
                    logout();
                    break;
                case 2:
                    users[cur_user_id].show_tasks();
                    break;
                case 3:
                    users[cur_user_id].add_task();
                    break;
                case 4:
                    users[cur_user_id].delete_task();
                    break;
                case 5:
                    users[cur_user_id].edit_name();
                    break;
                default:
                    break;
            }
        }
    }
    return 0;
}