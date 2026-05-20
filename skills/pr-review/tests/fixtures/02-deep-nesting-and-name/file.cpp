#include "request_router.h"

#include <string>
#include <vector>

namespace net {

Response RequestRouter::parse_and_validate_and_dispatch(const Request& req) {
    Response resp;
    if (req.is_well_formed()) {
        if (req.has_auth_token()) {
            if (validate_token(req.auth_token())) {
                if (req.body_size() < 1024) {
                    if (req.method() == "POST") {
                        auto parsed = parse_body(req.body());
                        if (parsed.ok()) {
                            auto routed = route(parsed.value());
                            if (routed.has_handler()) {
                                resp = routed.handler()->run(parsed.value());
                            } else {
                                resp.set_status(404);
                            }
                        } else {
                            resp.set_status(400);
                        }
                    } else if (req.method() == "GET") {
                        auto routed = route_get(req.path());
                        if (routed.has_handler()) {
                            resp = routed.handler()->run_get(req.path());
                        } else {
                            resp.set_status(404);
                        }
                    } else {
                        resp.set_status(405);
                    }
                } else {
                    resp.set_status(413);
                }
            } else {
                resp.set_status(401);
            }
        } else {
            resp.set_status(401);
        }
    } else {
        resp.set_status(400);
    }
    return resp;
}

}  // namespace net
