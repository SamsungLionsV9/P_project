package com.example.P_project.controller;

import com.example.P_project.entity.User;
import com.example.P_project.service.UserService;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class UserController {

    @Autowired
    private UserService userService;

    //로그인 기능(Login form
    @GetMapping("/login")
    public String loginForm() {
        return "login";
    }
    //로그인 처리
    @PostMapping("/login")
    public String login(@RequestParam String username,
                        @RequestParam String password,
                        HttpSession session) {
        User user = userService.findByUsername(username);
            //로그인 성공 시
        if (user != null && user.getPassword().equals(password)) {
            session.setAttribute("loginUser", user);
            return "redirect:/";
    }   else {
            return "redirect:/login?error";
        }
    }
    //로그아웃 기능
    @GetMapping
    public String logout(HttpSession session) {
        session.invalidate();
        return "redirect:/login";
    }
}
