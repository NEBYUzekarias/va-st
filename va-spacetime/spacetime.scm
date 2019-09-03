(use-modules (opencog) (opencog exec) (opencog query) (opencog python))
(add-to-load-path ".")

(python-eval "exec(open('spacetime.py').read())")

(define* (spt, name arg)
    (cog-execute!
        (ApplyLink
            (MethodOfLink
                (GroundedObjectNode "spatio-temporal-index")
                name)
                arg)))

(define* (va-spt-get-atom-by-time, timestamp)
     (spt,
          (ConceptNode "get_atom_by_time")
          (List (NumberNode timestamp))))

(define* (va-spt-add-atom,
          atom
          #:key
            (longitude 0)
            (latitude 0)
            (timestamp 0))

    (if (and (not (equal? longitude 0)) (not (equal? latitude 0)) )
        (cog-set-value! atom (Predicate "location") (FloatValue longitude latitude)))
    (if (not (equal? timestamp 0))
        (cog-set-value! atom (Predicate "timestamp") (FloatValue timestamp)))
    (spt,
         (ConceptNode "add_atom")
         (List atom)))


(define* (va-spt-get-atom-by-location, longitude latitude)
    (spt,
         (ConceptNode "get_atom_by_location")
         (ListLink
             (NumberNode longitude)
             (NumberNode latitude))))

(define* (va-spt-get-nearest-neighbors, longitude latitude #:key (distance 0))
      (spt,
           (ConceptNode "get_nearest_neighbors")
           (ListLink
               (NumberNode longitude)
               (NumberNode latitude)
               (NumberNode distance))))

(define* (va-spt-location-by-time, timestamp)
         (spt,
             (ConceptNode "get_location_by_time")
             (ListLink
                 (NumberNode timestamp))))
