package com.example.P_project.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import lombok.Getter;
import lombok.Setter;

//JPA에서 해당 클래스가 DB 테이블과 매핑
@Entity
@Getter
@Setter
public class User {

    @Id //기본키
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String username;    //사용자 아이디
    private String password;    //사용자 비밀번호
    private String email;       //이메일
    private String role;        //권한
    private String grade;       //회원 등급
}
