package br.edu.ibmec.chatbot_api.controllers;

import br.edu.ibmec.chatbot_api.models.Reserva;
import br.edu.ibmec.chatbot_api.repositories.ReservaRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/reservas")
public class ReservaController {
    private final ReservaRepository repo;
    public ReservaController(ReservaRepository repo) { this.repo = repo; }

    @PostMapping
    public ResponseEntity<Reserva> criar(@RequestBody Reserva r) {
        if (r.getCheckin() == null || r.getCheckout() == null) {
            return ResponseEntity.badRequest().build();
        }
        return ResponseEntity.ok(repo.save(r));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Reserva> obter(@PathVariable Long id) {
        return repo.findById(id).map(ResponseEntity::ok)
                   .orElse(ResponseEntity.notFound().build());
    }
}
