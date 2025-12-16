// [20251215_PERF] Java service sample for normalizer/taint benchmarks
package com.acme.service;

import org.springframework.transaction.annotation.Transactional;
import jakarta.validation.Valid;
import java.util.List;

public class Service<T extends Entity> extends BaseService implements Auditable {
    private final Repository<T> repo;

    public Service(Repository<T> repo) {
        this.repo = repo;
    }

    @Transactional
    public <R extends Number> R save(@Valid T entity) {
        repo.persist(entity);
        return null;
    }

    public List<T> findById(String id) {
        return repo.find("id", id);
    }

    class Inner {
        public void ping() {}
    }
}
