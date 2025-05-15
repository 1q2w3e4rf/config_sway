run() {
    if [ -f "$1" ]; then
        case "$1" in
            *.c)
                # Проверяем используемые библиотеки и компилируем с нужными флагами
                local cflags=""
                local libs=""

                # GTK3
                if grep -q "#include <gtk/gtk.h>" "$1"; then
                    cflags+=" $(pkg-config --cflags gtk+-3.0)"
                    libs+=" $(pkg-config --libs gtk+-3.0)"
                fi

                # SDL2
                if grep -q "#include <SDL2/SDL.h>" "$1"; then
                    cflags+=" $(sdl2-config --cflags)"
                    libs+=" $(sdl2-config --libs)"
                fi

                # OpenGL (GL/gl.h)
                if grep -q "#include <GL/gl.h>" "$1" || grep -q "#include <GL/glut.h>" "$1"; then
                    libs+=" -lGL -lGLU -lglut"
                fi

                # OpenSSL (для криптографии)
                if grep -q "#include <openssl/" "$1"; then
                    libs+=" -lssl -lcrypto"
                fi

                # libcurl (HTTP-запросы)
                if grep -q "#include <curl/curl.h>" "$1"; then
                    libs+=" -lcurl"
                fi

                # JSON-C (парсинг JSON)
                if grep -q "#include <json-c/json.h>" "$1"; then
                    libs+=" -ljson-c"
                fi

                # MySQL (работа с БД)
                if grep -q "#include <mysql/mysql.h>" "$1"; then
                    libs+=" -lmysqlclient"
                fi

                # PostgreSQL (работа с БД)
                if grep -q "#include <libpq-fe.h>" "$1"; then
                    libs+=" -lpq"
                fi

                # Математические функции (sin, cos и т. д.)
                if grep -q "#include <math.h>" "$1"; then
                    libs+=" -lm"
                fi

                # Стандартная компиляция (если не найдены специфичные библиотеки)
                if [ -z "$libs" ]; then
                    gcc -o "${1%.*}" "$1" && ./"${1%.*}"
                else
                    echo "Компиляция с флагами: gcc $cflags -o ${1%.*} $1 $libs"
                    gcc $cflags -o "${1%.*}" "$1" $libs && ./"${1%.*}"
                fi
                ;;
            *.py)
                python3 "$1"
                ;;
            *)
                echo "Неизвестный формат файла: $1"
                ;;
        esac
    else
        echo "Файл не существует: $1"
    fi
}
