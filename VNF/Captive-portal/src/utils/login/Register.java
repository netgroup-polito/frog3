package utils.login;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.URL;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import com.google.gson.Gson;




@WebServlet("/servlet_register")
public class Register extends HttpServlet {
	private static final long serialVersionUID = 1L;

	/**
	 * @see HttpServlet#HttpServlet()
	 */
	public Register() {
		super();
	}

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		System.out.println("INFO: Executing servlet_register...");
		@SuppressWarnings("unused")
		String salt=(String) request.getAttribute("salt");
		PrintWriter out = response.getWriter();
		String username=request.getParameter("username");
		String password=request.getParameter("password");
		String email=request.getParameter("email");//+request.getParameter("comboEmail");
		String success="";

		String ConfPath=(String) request.getAttribute("ConfigurationFile");
		File fileXML = new File(ConfPath+"FrogRelativePath.xml");
		DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
		DocumentBuilder dBuilder;
		Document doc=null;
		try {
			dBuilder = dbFactory.newDocumentBuilder();
			doc = dBuilder.parse(fileXML);
		} catch (ParserConfigurationException e1) {
			e1.printStackTrace();
		} catch (SAXException e) {
			e.printStackTrace();
		}
		
		doc.getDocumentElement().normalize();

		NodeList nodes = doc.getElementsByTagName("mgmtserver_address");
		Node node = nodes.item(0);
		Element element = (Element) node;
		NodeList nodes2 = element.getElementsByTagName("url").item(0).getChildNodes();
		Node node2 = (Node) nodes2.item(0);
		
		String mgmt_addr1 = node2.getNodeValue();
		String mgmt_addr=null;
		
		if(mgmt_addr1.contains("http://")){
			mgmt_addr=mgmt_addr1;
		}
		else{
			mgmt_addr="http://"+mgmt_addr1;
		}

		try{
			
			String temp="";
			String s_url=mgmt_addr+"/RegisterNewUser";
			System.out.println("Stiamo contattando: "+ s_url);
			
			temp+="username="+username+"&password="+password+"&email="+email;
			URL url = new URL(s_url+"?"+temp);
			System.out.println(s_url+"?"+temp);
			
			HttpURLConnection connection = (HttpURLConnection) url.openConnection();
		      	    
			connection.setConnectTimeout(10000);
			connection.setReadTimeout(10000);//timeoutLettura
		    connection.setRequestMethod("GET");
		    connection.connect();
			int status=connection.getResponseCode();//STATUS connession .----> status != httpURLConnection.HTTP_OK
			System.out.println(status);
			
			
			BufferedReader read = new BufferedReader(new InputStreamReader(connection.getInputStream()));
			
			String resp;
			
			while((resp=read.readLine())!=null){
				System.out.println(resp);
				success=new Gson().fromJson(resp,String.class);
				System.out.println(success+"<---------------------------------");			
				
			}
			read.close();
			
			
			}catch(IOException e){
				System.out.println("errore IOEXception");
				
			}

		System.out.println(email);
		if (success.equals("true")){

			//MailUtility.sendMail(email,u.toString());

			
			System.out.println("INFO: user '"+username+"' inserted");
			out.print("{success:true}");
		}else{
			System.out.println("INFO: username already exists");
			out.print("{success:false}");
		}
		System.out.println("INFO: ...servlet_register excecuted.");
	}
	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doGet(request, response);
	}

}