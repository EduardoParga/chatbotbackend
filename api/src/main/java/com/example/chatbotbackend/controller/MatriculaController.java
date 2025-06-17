package com.exemplo.chatbotbackend.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import com.exemplo.chatbotbackend.model.Matricula;
import com.exemplo.chatbotbackend.repository.MatriculaRepository;

@RestController
@RequestMapping("/api/matriculas")
@CrossOrigin
public class MatriculaController {

    @Autowired
    private MatriculaRepository repo;

    @PostMapping
    public String criarMatricula(@RequestBody Matricula matricula) {
        repo.save(matricula);
        return "Matrícula realizada com sucesso!";
    }
}
