package br.edu.ibmec.chatbot_api.repositories;

import br.edu.ibmec.chatbot_api.models.Reserva;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ReservaRepository extends JpaRepository<Reserva, Long> { }
