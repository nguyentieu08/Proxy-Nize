// =====================================================
// HEADSHOT PROXY - CLOUDFLARE WORKER
// Deploy lên Cloudflare Workers từ GitHub
// =====================================================

const REAL_SERVER = "https://loginbp.ggpolarbear.com";

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const path = url.pathname;

    // ====== FAKE VERSION (để game load được) ======
    if (path.includes("ver.php") || path.includes("version") || path.includes("favicon") || path.includes(".php")) {
      return new Response(
        JSON.stringify({
          code: 0,
          msg: "success",
          data: {
            version: "2.126.9",
            config: { enabled: true },
            server_time: Math.floor(Date.now() / 1000),
            region: "VN",
            whitelist_version: "1.7.0"
          }
        }),
        {
          headers: { "Content-Type": "application/json" },
          status: 200
        }
      );
    }

    // ====== SỬA REQUEST BẮN (HEADSHOT) ======
    const isAttack = ["shoot", "fire", "attack", "hit", "damage", "bullet"].some(k => path.includes(k));

    if (isAttack) {
      try {
        let body = await request.text();
        let data = JSON.parse(body);

        if (data && typeof data === "object") {
          // Sửa các trường hitbox
          if (data.hitbox) data.hitbox = "head";
          if (data.bodyPart) data.bodyPart = "head";
          if (data.part) data.part = "head";
          if (data.hitType) data.hitType = "head";
          data.isHeadshot = true;
          data.damage = 9999;
        }

        const forward = await fetch(REAL_SERVER + path, {
          method: request.method,
          headers: request.headers,
          body: JSON.stringify(data)
        });

        return new Response(forward.body, {
          status: forward.status,
          headers: forward.headers
        });
      } catch (e) {
        // Nếu lỗi parse JSON -> forward nguyên bản
        const forward = await fetch(REAL_SERVER + path, {
          method: request.method,
          headers: request.headers,
          body: request.body
        });
        return new Response(forward.body, {
          status: forward.status,
          headers: forward.headers
        });
      }
    }

    // ====== FORWARD CÁC REQUEST KHÁC ======
    const forward = await fetch(REAL_SERVER + path, {
      method: request.method,
      headers: request.headers,
      body: request.body
    });

    return new Response(forward.body, {
      status: forward.status,
      headers: forward.headers
    });
  }
};
