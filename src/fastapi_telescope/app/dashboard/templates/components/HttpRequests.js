export default {
  template: `
    <div v-if="loading === false">
      <h3 class="title">HTTP Requests</h3>

      <table class="request-table">
        <thead>
          <tr>
            <th>Method</th>
            <th>Path</th>
            <th>Status</th>
            <th>Response Time</th>
            <th>Happened</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in httpRequests" :key="request.id" @click="goToRequestDetails(request.id)">
            <td :class="getMethodClass(request.request_method)">{{ request.request_method }}</td>
            <td>{{ request.request_url }}</td>
            <td :class="getStatusClass(request.status_code)">{{ request.status_code }}</td>
            <td>{{ request.response_time }} ms</td>
            <td>
              <span :title="formatFullDatetime(request.created_at)">
                {{ formatRelativeTime(request.created_at) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination-controls">
        <button class="pagination-btn" @click="prevPage" :disabled="page <= 1">Previous</button>
        <span class="pagination-info">Page {{ page }} of {{ totalPages }}</span>
        <button class="pagination-btn" @click="nextPage" :disabled="page >= totalPages">Next</button>
      </div>
    </div>

    <div v-else>
      <h2 class="title">Loading...</h2>
    </div>
  `,
  data() {
    return {
      httpRequests: [],
      loading: true,
      page: 1,
      size: 10,
      totalPages: 1,
    };
  },
  watch: {
    '$route.query.page': {
      immediate: true,
      handler(newVal) {
        const newPage = parseInt(newVal) || 1;
        if (newPage !== this.page) {
          this.page = newPage;
          this.fetchRequests();
        }
      }
    }
  },
  mounted() {
    this.fetchRequests();
  },
  methods: {
    async fetchRequests() {
      this.loading = true;
      try {
        const response = await axios.get(`/http-requests`, {
          params: {
            page: this.page,
            size: this.size
          }
        });
        this.httpRequests = response.data.items;
        this.totalPages = response.data.pages;
      } catch (error) {
        console.error('Error fetching HTTP requests:', error);
      } finally {
        this.loading = false;
      }
    },
    changePage(newPage) {
      if (newPage !== this.page && newPage >= 1 && newPage <= this.totalPages) {
        this.$router.push({
          name: "http-requests",
          query: { ...this.$route.query, page: newPage }
        });
      }
    },
    nextPage() {
      this.changePage(this.page + 1);
    },
    prevPage() {
      this.changePage(this.page - 1);
    },
    goToRequestDetails(requestId) {
      this.$router.push({ name: "http-request-detail", params: { id: requestId } });
    },
    formatRelativeTime(datetime) {
      const userTimezone = dayjs.tz.guess();
      return dayjs.utc(datetime).tz(userTimezone).fromNow();
    },
    formatFullDatetime(datetime) {
      const userTimezone = dayjs.tz.guess();
      return dayjs.utc(datetime).tz(userTimezone).format("YYYY-MM-DD HH:mm:ss [Z]");
    },
    getStatusClass(statusCode) {
      if (statusCode >= 200 && statusCode < 300) return "status-green";
      if (statusCode >= 300 && statusCode < 400) return "status-blue";
      if (statusCode >= 400 && statusCode < 500) return "status-orange";
      if (statusCode >= 500) return "status-red";
    },
    getMethodClass(method) {
      if (method === "GET") return "method-grey";
      if (method === "POST") return "method-blue";
      if (method === "PUT") return "method-green";
      if (method === "DELETE") return "method-red";
    }
  }
};