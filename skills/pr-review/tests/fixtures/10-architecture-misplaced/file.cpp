// New file: src/util/db_connection.cpp
// Adds a database-connection helper into the generic "util" module.

#include "util/db_connection.h"

#include "core/logger.h"      // existing dependency: core -> util
#include "net/http_client.h"  // NEW: util -> net (introduces cycle: net -> util -> net)

#include <pqxx/pqxx>          // NEW: util now depends on libpqxx (Postgres)

namespace util {

class DbConnection {
public:
    DbConnection(std::string conn_str, net::HttpClient* notifier);
    ~DbConnection();

    pqxx::connection& raw();
    void notify_observers(const std::string& event);

private:
    pqxx::connection m_conn;
    net::HttpClient* m_notifier;
    core::Logger m_log;
};

}  // namespace util
