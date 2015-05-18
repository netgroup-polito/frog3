
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URL;
import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.HttpClientBuilder;
import org.json.JSONObject;
import java.io.InputStream;
import java.util.Properties;

/**
 * 
 * Servlet implementation class Update
 */
public class Update extends HttpServlet {
	String orchestrator_port;
	String orchestrator_ip;
	ServletContext context;
	
	private static final long serialVersionUID = 1L;
	/**
	 * 
	 * @see HttpServlet#HttpServlet()
	 */
	public Update() {
		super();
		//getConf();
	}

	private void getConf() {
		context = getServletContext();
		
		InputStream input = context.getResourceAsStream(
				"/WEB-INF" + "/captive_portal.properties");
		Properties p = new Properties();
		try {
			p.load(input);
		} catch (IOException e) {
			e.printStackTrace();
			throw new RuntimeException(
					"We encounter an unhandable problem in the request processing. Contact the system administrator.");
		}

		orchestrator_ip = (String) p.getProperty("orchestrator_ip");
		orchestrator_port = (String) p.getProperty("orchestrator_port");
	}

	/**
	 * 
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse
	 *      response)
	 */
	protected void doGet(HttpServletRequest request,
			HttpServletResponse response) throws ServletException, IOException
	{
		response.setContentType("text/xml");
		response.setHeader("Cache-Control", "no-cache");
		String status = getOrchestratorStatus(response, request);
		System.out.println("Update: " + status);
		response.getWriter().write(status);
	}

	private String getOrchestratorStatus(HttpServletResponse response, HttpServletRequest request)
	{
		try 
		{
			HttpSession session = request.getSession();
	    	ServletContext sc = session.getServletContext();
	    	String req_URI = (String) session.getAttribute("requested_path");
			String CP_ex_IP = (String)sc.getAttribute("captive_portal_ip_external");
	    	String token = (String) session.getAttribute("Keystone_token");

			HttpClient httpClient = HttpClientBuilder.create().build(); 

			URL temp = new URL("http","orchestrator",8000,"/orchestrator");
			//URL temp = new URL("http", orchestrator_ip,Integer.parseInt(orchestrator_port),"/orchestrator");

			HttpGet putRequest = new HttpGet(temp.toString());

			putRequest.setHeader("Accept", "application/json");

			putRequest.setHeader("X-Auth-Token", token);
			
			HttpResponse orchestrator_response = httpClient.execute(putRequest);

			System.out.println(orchestrator_response.getStatusLine().toString());
			System.out.println("CIAO"+token);
			int orch_response_status_code = orchestrator_response.getStatusLine().getStatusCode();
			if ((orch_response_status_code == 201) || (orch_response_status_code == 202))
			{
				BufferedReader br = new BufferedReader(
						new InputStreamReader((orchestrator_response.getEntity().getContent())));

				String json_response = br.readLine();
			   	if (json_response != null)
			   	{
			   		JSONObject jsonObject = new JSONObject(json_response);
			   		jsonObject.append("captive_portal_ip",CP_ex_IP);
			   		jsonObject.append("requested_URI", req_URI);
	
			   		String r = jsonObject.toString();
					if (orch_response_status_code == 201)
					{

//			        	if (sendDeployOKMsgToTheController(request.getRemoteAddr(),session) == false)
//			        	{
//			    			System.err.println("Problem with the controller comunication");
//			    			throw new RuntimeException("We encounter an unhandable problem in the request processing. Contact the system administrator.");
//			        
//			        	}

						response.setHeader("Connection","close");
					}
			   		if (r != null)
			   			return r;
			   	}
			} else
			{

				response.setStatus(orchestrator_response.getStatusLine().getStatusCode());
				return "Some error occurs";
			}

		  } catch (ClientProtocolException e) {

				System.err.println("HTTP Put Error: "+e.getMessage());
				throw new RuntimeException("We encounter an unhandable problem in the request processing. Contact the system administrator.");

		  } catch (IOException e) {

				System.err.println(e.getMessage());
				throw new RuntimeException("We encounter an unhandable problem in the request processing. Contact the system administrator.");
		  }
		  response.setStatus(500);
		  return "Some error occurs";
	}

	// private boolean sendDeployOKMsgToTheController(String ip,HttpSession
	// session) {
	// MessageWithIP msg = new MessageWithIP(ip,
	// null,Message.MsgType.Deploy_OK);
	// try {
	// String s = sendMessageToTheController(msg,session);
	// JSONObject jsonObject = new JSONObject(s);
	// Message m = new Message(jsonObject);
	//
	// if (m.getMsg_type() == Message.MsgType.Deploy_OK_Resp)
	// return true;
	// else
	// return false;
	// //JSONObject jsonObject = new JSONObject(s);
	//
	// //return new AuthResponseMessage(jsonObject);
	// } catch (IOException e) {
	// System.err.println("Socket or Input/Output stream closing error. "+e.getMessage());
	// throw new
	// RuntimeException("We encounter an unhandable problem in the request processing. Contact the system administrator.");
	// }
	// }
	//
	// private String sendMessageToTheController(MessageWithIP msg,HttpSession
	// session) throws IOException
	// {
	// String hostName =
	// (String)session.getServletContext().getAttribute("controller_ip");
	// int portNumber =
	// Integer.parseInt((String)session.getServletContext().getAttribute("controller_port"));
	// Socket mySocket = null;
	// PrintWriter out = null;
	// BufferedReader in = null;
	//
	// try {
	// mySocket = new Socket(hostName, portNumber);
	// mySocket.setSoTimeout(5000);
	// out =
	// new PrintWriter(mySocket.getOutputStream(), true);
	// in =
	// new BufferedReader(
	// new InputStreamReader(mySocket.getInputStream()));
	//
	// JSONObject jsonObject = msg.getJSON();
	// out.println(jsonObject.toString());
	// String server_response;
	//
	// server_response = in.readLine();
	// if (server_response != null)
	// return server_response;
	// else
	// {
	// System.err.println("No response from the controller");
	// throw new
	// RuntimeException("We encounter an unhandable problem in the request processing. Contact the system administrator.");
	// }
	//
	// }catch (java.net.SocketTimeoutException e)
	// {
	// System.err.println("Timeout expired. "+e.getMessage());
	// throw new
	// RuntimeException("We encounter an unhandable problem in the request processing. Contact the system administrator.");
	// }
	// catch (Exception e)
	// {
	// System.err.println(e.getMessage());
	// throw new
	// RuntimeException("We encounter an unhandable problem in the request processing. Contact the system administrator.");
	// }finally
	// {
	// if (out!=null) out.close();
	// if (in!=null) in.close();
	// if (mySocket!=null) mySocket.close();
	// }
	//
	//
	// }
}
