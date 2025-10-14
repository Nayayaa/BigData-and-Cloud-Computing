package br.edu.ibmec.chatbot_api.models;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDate;

@Data
@Entity
@Table(name = "reservas")
public class Reserva {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String nome;
    private String email;
    private LocalDate checkin;
    private LocalDate checkout;
    private Integer hospedes;
    private String tipoQuarto;
    @Column(columnDefinition = "TEXT")
    private String chatHistory;
}
