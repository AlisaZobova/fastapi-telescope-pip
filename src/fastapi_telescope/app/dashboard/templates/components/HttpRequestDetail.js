export default {
  template: `
    <div class="request-details" v-if="loading !== true">
      <div class="section">
        <h2>Request Details</h2>
        <table>
          <tbody>
            <tr>
              <td>Id:</td>
              <td>{{ httpRequest.id }}</td>
            </tr>
            <tr>
              <td>Time:</td>
              <td>
                <span :title="formatFullDatetime(httpRequest.created_at)">
                  {{ formatRelativeTime(httpRequest.created_at) }}
                </span>
              </td>
            </tr>
            <tr>
              <td>Method:</td>
              <td>{{ httpRequest.request_method }}</td>
            </tr>
            <tr>
              <td>Path:</td>
              <td>{{ httpRequest.request_url }}</td>
            </tr>
            <tr>
              <td>Status:</td>
              <td>{{ httpRequest.status_code }}</td>
            </tr>
            <tr>
              <td>Duration:</td>
              <td>{{ httpRequest.response_time }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="section" v-if="httpRequest.user_id">
        <h2>Authenticated User</h2>
        <table>
          <tbody>
            <tr>
              <td>ID:</td>
              <td>{{ httpRequest.user_id }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="section" v-if="httpRequest.request_method !== 'GET'">
        <h2>Payload</h2>
        <pre class="json-container"><div class="json-inner"><span>{{ formatJson(httpRequest.request_body) }}</span></div></pre>
      </div>
      
      <div class="section" v-if="httpRequest.response_body">
        <h2>Response</h2>
        <pre class="json-container"><div class="json-inner width-100"><span>{{ formatJson(httpRequest.response_body) }}</span></div></pre>
      </div>
      
      <div class="section" v-if="httpRequest.exception_message">
        <h2>Exception Message</h2>
        <pre class="width-100">{{ httpRequest.exception_message }}</pre>
      </div>
            
      <div class="section" v-if="httpRequest.stack_trace">
        <h2>Stack Trace</h2>
        <pre class="width-100">{{ httpRequest.stack_trace }}</pre>
      </div>

      <div v-if="dbQueries.length > 0" class="section">
        <h2>DB Queries</h2>
        <table>
          <tbody>
            <tr v-for="query in dbQueries" :key="query.id" @click="goToQueryDetails(query.id)">
              <td class="width-100" v-if="query.db_query.length<500">{{ query.db_query }}</td>
              <td class="width-100" v-else><span :title="query.db_query">{{ query.db_query.substring(0,500)+"..." }}</span></td>
              <td>{{ query.db_query_time }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else>
      <h2 class="title">Loading...</h2>
    </div>
  `,
  data() {
    return {
      httpRequest: {},
      dbQueries: [],
      loading: true,
    };
  },
  async created() {
    const requestId = this.$route.params.id;
    try {
      const [requestResponse, queriesResponse] = await Promise.all([
        axios.get(`/http-requests/${requestId}`),
        axios.get(`/http-requests/${requestId}/db-queries`)
      ]);

      this.httpRequest = requestResponse.data;
      this.dbQueries = queriesResponse.data;
    } catch (error) {
      console.error('Error fetching HTTP request details:', error);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    goToQueryDetails(queryId) {
      this.$router.push({ name: 'db-query-detail', params: { id: queryId } });
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
    formatJson(content) {
      try {
        return JSON.stringify(JSON.parse(content), null, 4);
      } catch (e) {
        return content;
      }
    }
  }
};