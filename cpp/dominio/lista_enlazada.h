#ifndef LISTA_ENLAZADA_H
#define LISTA_ENLAZADA_H

#include <cstddef>
#include <stdexcept>
#include <utility>
#include <functional>

namespace pita {

template <typename T>
struct Nodo {
    T dato;
    Nodo* anterior;
    Nodo* siguiente;

    explicit Nodo(const T& valor) : dato(valor), anterior(nullptr), siguiente(nullptr) {}
    explicit Nodo(T&& valor) : dato(std::move(valor)), anterior(nullptr), siguiente(nullptr) {}
};

template <typename T>
class ListaEnlazada {
private:
    Nodo<T>* cabeza;
    Nodo<T>* cola;
    size_t longitud;

public:
    // Iteradores
    class Iterator {
    private:
        Nodo<T>* actual;
    public:
        using iterator_category = std::bidirectional_iterator_tag;
        using value_type = T;
        using difference_type = std::ptrdiff_t;
        using pointer = T*;
        using reference = T&;

        explicit Iterator(Nodo<T>* nodo = nullptr) : actual(nodo) {}

        reference operator*() const { return actual->dato; }
        pointer operator->() const { return &(actual->dato); }

        Iterator& operator++() {
            if (actual) actual = actual->siguiente;
            return *this;
        }

        Iterator operator++(int) {
            Iterator temp = *this;
            ++(*this);
            return temp;
        }

        Iterator& operator--() {
            if (actual) actual = actual->anterior;
            return *this;
        }

        Iterator operator--(int) {
            Iterator temp = *this;
            --(*this);
            return temp;
        }

        bool operator==(const Iterator& otro) const { return actual == otro.actual; }
        bool operator!=(const Iterator& otro) const { return actual != otro.actual; }

        Nodo<T>* getNodo() const { return actual; }
    };

    class ConstIterator {
    private:
        const Nodo<T>* actual;
    public:
        using iterator_category = std::bidirectional_iterator_tag;
        using value_type = const T;
        using difference_type = std::ptrdiff_t;
        using pointer = const T*;
        using reference = const T&;

        explicit ConstIterator(const Nodo<T>* nodo = nullptr) : actual(nodo) {}
        ConstIterator(const Iterator& it) : actual(it.getNodo()) {}

        reference operator*() const { return actual->dato; }
        pointer operator->() const { return &(actual->dato); }

        ConstIterator& operator++() {
            if (actual) actual = actual->siguiente;
            return *this;
        }

        ConstIterator operator++(int) {
            ConstIterator temp = *this;
            ++(*this);
            return temp;
        }

        ConstIterator& operator--() {
            if (actual) actual = actual->anterior;
            return *this;
        }

        ConstIterator operator--(int) {
            ConstIterator temp = *this;
            --(*this);
            return temp;
        }

        bool operator==(const ConstIterator& otro) const { return actual == otro.actual; }
        bool operator!=(const ConstIterator& otro) const { return actual != otro.actual; }
    };

    // Constructores y Destructor
    ListaEnlazada() : cabeza(nullptr), cola(nullptr), longitud(0) {}

    ListaEnlazada(const ListaEnlazada& otra) : cabeza(nullptr), cola(nullptr), longitud(0) {
        for (const auto& item : otra) {
            push_back(item);
        }
    }

    ListaEnlazada(ListaEnlazada&& otra) noexcept 
        : cabeza(otra.cabeza), cola(otra.cola), longitud(otra.longitud) {
        otra.cabeza = nullptr;
        otra.cola = nullptr;
        otra.longitud = 0;
    }

    ListaEnlazada& operator=(const ListaEnlazada& otra) {
        if (this != &otra) {
            clear();
            for (const auto& item : otra) {
                push_back(item);
            }
        }
        return *this;
    }

    ListaEnlazada& operator=(ListaEnlazada&& otra) noexcept {
        if (this != &otra) {
            clear();
            cabeza = otra.cabeza;
            cola = otra.cola;
            longitud = otra.longitud;
            otra.cabeza = nullptr;
            otra.cola = nullptr;
            otra.longitud = 0;
        }
        return *this;
    }

    ~ListaEnlazada() {
        clear();
    }

    // Capacidad
    bool empty() const noexcept { return longitud == 0; }
    size_t size() const noexcept { return longitud; }
    size_t tamano() const noexcept { return longitud; }
    T& obtener(size_t indice) { return at(indice); }
    const T& obtener(size_t indice) const { return at(indice); }

    // Modificadores
    void push_back(const T& valor) {
        Nodo<T>* nuevo = new Nodo<T>(valor);
        if (empty()) {
            cabeza = cola = nuevo;
        } else {
            cola->siguiente = nuevo;
            nuevo->anterior = cola;
            cola = nuevo;
        }
        longitud++;
    }

    void push_back(T&& valor) {
        Nodo<T>* nuevo = new Nodo<T>(std::move(valor));
        if (empty()) {
            cabeza = cola = nuevo;
        } else {
            cola->siguiente = nuevo;
            nuevo->anterior = cola;
            cola = nuevo;
        }
        longitud++;
    }

    void push_front(const T& valor) {
        Nodo<T>* nuevo = new Nodo<T>(valor);
        if (empty()) {
            cabeza = cola = nuevo;
        } else {
            nuevo->siguiente = cabeza;
            cabeza->anterior = nuevo;
            cabeza = nuevo;
        }
        longitud++;
    }

    void pop_front() {
        if (empty()) return;
        Nodo<T>* temp = cabeza;
        cabeza = cabeza->siguiente;
        if (cabeza) {
            cabeza->anterior = nullptr;
        } else {
            cola = nullptr;
        }
        delete temp;
        longitud--;
    }

    void pop_back() {
        if (empty()) return;
        Nodo<T>* temp = cola;
        cola = cola->anterior;
        if (cola) {
            cola->siguiente = nullptr;
        } else {
            cabeza = nullptr;
        }
        delete temp;
        longitud--;
    }

    void clear() noexcept {
        Nodo<T>* actual = cabeza;
        while (actual != nullptr) {
            Nodo<T>* siguiente = actual->siguiente;
            delete actual;
            actual = siguiente;
        }
        cabeza = cola = nullptr;
        longitud = 0;
    }

    // Acceso
    T& front() {
        if (empty()) throw std::out_of_range("Lista vacia");
        return cabeza->dato;
    }

    const T& front() const {
        if (empty()) throw std::out_of_range("Lista vacia");
        return cabeza->dato;
    }

    T& back() {
        if (empty()) throw std::out_of_range("Lista vacia");
        return cola->dato;
    }

    const T& back() const {
        if (empty()) throw std::out_of_range("Lista vacia");
        return cola->dato;
    }

    T& at(size_t indice) {
        if (indice >= longitud) throw std::out_of_range("Indice fuera de rango");
        Nodo<T>* actual = cabeza;
        for (size_t i = 0; i < indice; ++i) {
            actual = actual->siguiente;
        }
        return actual->dato;
    }

    const T& at(size_t indice) const {
        if (indice >= longitud) throw std::out_of_range("Indice fuera de rango");
        const Nodo<T>* actual = cabeza;
        for (size_t i = 0; i < indice; ++i) {
            actual = actual->siguiente;
        }
        return actual->dato;
    }

    T& operator[](size_t indice) {
        return at(indice);
    }

    const T& operator[](size_t indice) const {
        return at(indice);
    }

    // Iteradores begin/end
    Iterator begin() noexcept { return Iterator(cabeza); }
    Iterator end() noexcept { return Iterator(nullptr); }
    ConstIterator begin() const noexcept { return ConstIterator(cabeza); }
    ConstIterator end() const noexcept { return ConstIterator(nullptr); }
    ConstIterator cbegin() const noexcept { return ConstIterator(cabeza); }
    ConstIterator cend() const noexcept { return ConstIterator(nullptr); }

    // Utilidades de búsqueda y filtrado
    template <typename Predicate>
    Iterator find_if(Predicate pred) {
        for (auto it = begin(); it != end(); ++it) {
            if (pred(*it)) return it;
        }
        return end();
    }

    template <typename Predicate>
    ConstIterator find_if(Predicate pred) const {
        for (auto it = cbegin(); it != cend(); ++it) {
            if (pred(*it)) return it;
        }
        return cend();
    }

    template <typename Predicate>
    bool remove_if(Predicate pred) {
        bool eliminado = false;
        Nodo<T>* actual = cabeza;
        while (actual != nullptr) {
            if (pred(actual->dato)) {
                Nodo<T>* a_borrar = actual;
                actual = actual->siguiente;

                if (a_borrar->anterior) {
                    a_borrar->anterior->siguiente = a_borrar->siguiente;
                } else {
                    cabeza = a_borrar->siguiente;
                }

                if (a_borrar->siguiente) {
                    a_borrar->siguiente->anterior = a_borrar->anterior;
                } else {
                    cola = a_borrar->anterior;
                }

                delete a_borrar;
                longitud--;
                eliminado = true;
            } else {
                actual = actual->siguiente;
            }
        }
        return eliminado;
    }
};

} // namespace pita

#endif // LISTA_ENLAZADA_H
