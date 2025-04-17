export default {
  template: `
    <div v-if="loading === false">
      <h2 class="title">Query Details</h2>

      <div class="section">
        <table>
          <tbody>
            <tr>
              <td>Query id:</td>
              <td>{{dbQuery.id}}</td>
            </tr>
            <tr>
              <td>Happened:</td>
              <td>
                <span :title="formatFullDatetime(dbQuery.created_at)">
                  {{ formatRelativeTime(dbQuery.created_at) }}
                </span>
              </td>
            </tr>
            <tr>
              <td>Level:</td>
              <td>{{ dbQuery.level }}</td>
            </tr>
            <tr>
              <td>Query time:</td>
              <td>{{ dbQuery.db_query_time }}</td>
            </tr>
            <tr>
              <td>Request:</td>
              <td class="link" @click="goToRequestDetails(dbQuery.log_http_request_id)">{{ dbQuery.log_http_request_id }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="section">
        <h2>Query</h2>
        <pre class="width-100">{{ dbQuery.db_query }}</pre>
      </div>
    </div>

    <div v-else>
      <h2 class="title">Loading...</h2>
    </div>
  `,
  data() {
    return {
      dbQuery: {},
      loading: true,
    }
  },
  async created() {
    const requestId = this.$route.params.id;
    try {
      const response = await axios.get(`/db-queries/${requestId}`);
      this.dbQuery = response.data;
    } catch (error) {
      console.error('Error fetching DB query details:', error);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    goToRequestDetails(requestId) {
      this.$router.push({ name: 'http-request-detail', params: { id: requestId } });
    },
    formatRelativeTime(datetime) {
      const userTimezone = dayjs.tz.guess();
      const localTime = dayjs.utc(datetime).tz(userTimezone);
      return localTime.fromNow();
    },
    formatFullDatetime(datetime) {
      const userTimezone = dayjs.tz.guess();
      return dayjs.utc(datetime).tz(userTimezone).format("YYYY-MM-DD HH:mm:ss [Z]");
    },
  }
};