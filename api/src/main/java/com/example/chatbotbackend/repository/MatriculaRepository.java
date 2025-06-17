package com.exemplo.chatbotbackend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import com.exemplo.chatbotbackend.model.Matricula;

public interface MatriculaRepository extends JpaRepository<Matricula, Long> {}
