package utils.login;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.Socket;
import java.net.URL;
import java.net.UnknownHostException;
import java.util.Hashtable;

import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Source;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerConfigurationException;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathFactory;
import javax.xml.xpath.XPathConstants;



/**
 * Servlet implementation class Logout
 */
@WebServlet("/servlet_logout")
public class Logout extends HttpServlet {
	private static final long serialVersionUID = 1L;

	/**
	 * @see HttpServlet#HttpServlet()
	 */
	public Logout() {
		super();
	}

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	@SuppressWarnings("unchecked")
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		System.out.println("INFO: Executing servlet_logout...");
		//Session s=(Session)request.getAttribute("Session");
		
		String idPEX=null;
		
		System.out.println("user = " + request.getParameter("username"));
		
		String username = (String) request.getParameter("username");

		DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
		DocumentBuilder dBuilder;
		Document doc=null;
		
				//read the file with the relative path
				String ConfPath=(String) request.getAttribute("ConfigurationFile");
				File fileXML = new File(ConfPath+"FrogRelativePath.xml");
				dbFactory = DocumentBuilderFactory.newInstance();
				
				doc=null;
				try {
					dBuilder = dbFactory.newDocumentBuilder();
					doc = dBuilder.parse(fileXML);
				} catch (ParserConfigurationException e1) {
					e1.printStackTrace();
				} catch (SAXException e) {
					e.printStackTrace();
				}
				
				doc.getDocumentElement().normalize();
				
				NodeList nodes5 = doc.getElementsByTagName("active_pex_configfile");
				Node node5 = nodes5.item(0);
				Element element2 = (Element) node5;
				NodeList nodes4 = element2.getElementsByTagName("url").item(0).getChildNodes();
				Node node4 = (Node) nodes4.item(0);
				String line4=node4.getNodeValue();
		
///////////////////////////////////////////////////////////////////////////////	
//<-------------------------------------- Starting to read ActivePEX.xml (it contains all active pex at the moment)	 
		
		
		//find the file
		fileXML = new File(System.getProperty("catalina.base")+"/"+line4+"ActivePex.xml");
		
		//read the file
		DocumentBuilderFactory dbFactory1 = DocumentBuilderFactory.newInstance();
		DocumentBuilder dBuilder1;
		Document doc1=null;
		try {
			dBuilder1 = dbFactory1.newDocumentBuilder();
			doc1 = dBuilder1.parse(fileXML);
		} catch (ParserConfigurationException e1) {
			e1.printStackTrace();
		} catch (SAXException e) {
			e.printStackTrace();
		}
		doc1.getDocumentElement().normalize();
		
		
		
		//find the MAC of the user that is logged
		
		String MacValue=null;
		
		if(request.getParameter("MAC")!=null){			
			MacValue = (String) request.getParameter("MAC");
			System.out.println("[DEBUG] MAC passed : "+MacValue);
		}
		else {
			System.out.println("[DEBUG] MAC not passed: searching with DHCP");
			String ip2=request.getRemoteAddr();
			
			//<--------------------------------------Parte connessione con DHCP
			String string_out3=new String();
			string_out3+="GET who is "+ip2+"\r\n";
			
			try{
				Socket so=new Socket("127.0.0.1", 9876);
				DataOutputStream os= new DataOutputStream(so.getOutputStream());
				BufferedReader is = new BufferedReader(new InputStreamReader(so.getInputStream()));
				
				os.writeBytes(string_out3);
				
				String responseline=null;
				while ((responseline=is.readLine())!=null){
					MacValue=responseline;
					System.out.println("[DEBUG] DHCP response:"+responseline);
					
				}
				System.out.println("[DEBUG] MAC after DCHP response(empty if not response):"+MacValue);
				if(MacValue==null){
					System.out.println("[DEBUG] Error in DHCP response: MAC address not founded");
					System.exit(1);
				}
				os.close();
				is.close();
				so.close();
			
			}catch(UnknownHostException e){
				System.out.println("Host unknown");
			}catch(IOException e){
				System.out.println("[DEBUG] Error: DHCP not response: stopping LocalServer");
				System.exit(1);					
			}
		
		}
		
		/*
		*	find in the xml file if exist a pex associated to MacValue and username and remove it
		*/
		
		NodeList nodes1 = doc1.getElementsByTagName("PEX");
		/*
		*	For each element "PEX" into the file
		*/
		for (int i=0 ; i< nodes1.getLength(); i++)
		{
			Element e = (Element) nodes1.item(i);
			/*
			*	If this PEX is of a specific user and has a specific mac address...
			*/
			if (e.getAttribute("MAC").equals(MacValue) && e.getAttribute("user").equals(username)) 
			{
				/*
				*	...remove it!
				*/
				System.out.println ("username found = "+e.getAttribute("user"));
				idPEX= e.getAttribute("PEXID");
				System.out.println ("PEX ID found = "+idPEX);
				NodeList nodes2 = doc1.getElementsByTagName("ActivePEX");
				Element e1 = (Element) nodes2.item(i);
				e1.removeChild(e);
			}
		}
		
		/*
		*	When an xml node is removed, into the file remains an empty row. The following lines of code remove this 
		*	empty row.
		*/
		try
		{
			XPath xp = XPathFactory.newInstance().newXPath();
			NodeList nl = (NodeList) xp.evaluate("//text()[normalize-space(.)='']", doc1, XPathConstants.NODESET);

			for (int i=0; i < nl.getLength(); ++i) 
			{
				Node node = nl.item(i);
				node.getParentNode().removeChild(node);
			}
		} 
		catch (Exception xpee)
		{
			xpee.printStackTrace();
		}
		
		
		//write the new xml file
		PrintStream stream=new PrintStream(fileXML);
		TransformerFactory xformFactory = TransformerFactory.newInstance ();
		Transformer idTransform;
		try {
			idTransform = xformFactory.newTransformer ();
			//idTransform.setOutputProperty(OutputKeys.DOCTYPE_SYSTEM,"access.dtd");
			idTransform.setOutputProperty(OutputKeys.INDENT, "yes");
			Source input = new DOMSource (doc1);
			StreamResult output = new StreamResult (stream);
			idTransform.transform (input, output);
		} catch (TransformerConfigurationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (TransformerException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		
///////////////////////////////////////////////////////////////////////////////	
//<-------------------------------------- Starting to kill the pex	 		
		
			
		
			
		
		
			//read the absolute path to frog folder
			NodeList nodes6 = doc.getElementsByTagName("absolute_path_frog");
			Node node1 = nodes6.item(0);
			Element element1 = (Element) node1;
			NodeList nodes3 = element1.getElementsByTagName("url").item(0).getChildNodes();
			Node node3 = (Node) nodes3.item(0);
			String line3=node3.getNodeValue();
	
			//read the path for script folder
			NodeList nodes = doc.getElementsByTagName("script_path");
			Node node = nodes.item(0);
			Element element = (Element) node;
			NodeList nodes2 = element.getElementsByTagName("url").item(0).getChildNodes();
			Node node2 = (Node) nodes2.item(0);
			String line=node2.getNodeValue();
		

			System.out.println("bash "+line3+line+"deletePEX.sh "+idPEX +" ");
			
			//execute deletePEX script
			Runtime.getRuntime().exec("bash "+line3+line+"deletePEX.sh "+idPEX +" ");

			ServletContext context = getServletContext();
			Hashtable<Integer, HashTabValue> VertPEX=(Hashtable<Integer, HashTabValue>)context.getAttribute("HashTab");
			int key=Integer.parseInt(idPEX);
			VertPEX.remove(key);
			if(VertPEX.isEmpty()){
				System.out.println("Svuotata");
			}
			this.getServletContext().setAttribute("HashTab", VertPEX);
			
			
			
///////////////////////////////////////////////////////////////////////////////	
//<-------------------------------------- Deleting PEX from mgmtserver				
			
			
			System.out.println("INFO: Deleting PEX"+ idPEX +": remove it from mgmtserver");
			
			//read the relative path with mgmt address
			nodes = doc.getElementsByTagName("mgmtserver_address");
			node = nodes.item(0);
			element = (Element) node;
			nodes2 = element.getElementsByTagName("url").item(0).getChildNodes();
			node2 = (Node) nodes2.item(0);
						
			String mgmt_addr1 = node2.getNodeValue();
			String mgmt_addr=null;
			
			if(mgmt_addr1.contains("http://")){
				mgmt_addr=mgmt_addr1;
			}
			else{
				mgmt_addr="http://"+mgmt_addr1;
			}
			
			
			//read the relative path with local address
			nodes1 = doc.getElementsByTagName("localserver_address");
			node1 = nodes1.item(0);
			element1 = (Element) node1;
			nodes3 = element1.getElementsByTagName("url").item(0).getChildNodes();
			node3 = (Node) nodes3.item(0);	
			
			String url1 = node3.getNodeValue();
			
			String addr = null;
			
			try{
				addr = url1.split("//")[1];
			}
			catch(Exception e){
				addr=url1;
			}
			
			String ip = addr.split(":")[0];
			
			try{
				URL url = new URL(mgmt_addr+"/Delete_PEX_at_IDPEX?ipaddr="+ip+"&idPEX="+idPEX);

				System.out.println("[DEBUG] URL contacted: "+ url.toString());
				
				

				HttpURLConnection connection = (HttpURLConnection) url.openConnection();
			    
				//http connect to that servlet
				
				connection.setConnectTimeout(10000);
				connection.setReadTimeout(10000);//timeoutLettura
			    connection.setRequestMethod("GET");
			    connection.connect();
			    int status=connection.getResponseCode();//STATUS connession .----> status != httpURLConnection.HTTP_OK
				System.out.println(status);
				
				
				BufferedReader read = new BufferedReader(new InputStreamReader(connection.getInputStream()));
				
				String resp;
				
				while((resp=read.readLine())!=null){				//read the response of the servlet (the format is: port1,port2,port3 ecc.)
					line = resp;
					System.out.println("[DEBUG] Delete_PEX_at_IDPEX: Response from MgmtServer "+line);
					
				}	
				read.close();
			}catch (MalformedURLException e)
			{
				System.out.println("Malformed exception");
				e.printStackTrace();
			}catch (IOException e){
				System.out.println("IO exception");
				e.printStackTrace();
			}
			
			Cookie cookie1 = new Cookie("user", "bla");
			cookie1.setMaxAge(0);
			cookie1.setPath("/");
			response.addCookie(cookie1); 
			PrintWriter out = response.getWriter();
		
			out.print("{success:true}");
			
			/*
			 
			set the Access-Control-Allow-Origin header of the response to * (= any). This allow the cross-domain http request.
			Access-Control-Allow-Origin Header: this header is used to specify which web sites can participate in cross-origin resource sharing.			

			A returned resource may have one Access-Control-Allow-Origin header, with the following syntax:

			Access-Control-Allow-Origin: <origin> | *
			
			The origin parameter specifies a URI that may access the resource.  
			The browser must enforce this.  
			For requests without credentials, the server may specify "*" as a wildcard, there by allowing any origin to access the resource.
			
			*/
			
			response.setHeader("Access-Control-Allow-Origin", "*");

			System.out.println("[DEBUG] Access-Control-Allow-Origin header = "+response.getHeader("Access-Control-Allow-Origin"));
			
			request.getSession().invalidate();
			
			out.flush();
			System.out.println("INFO: ...servlet_logout excecuted.");
		
		

	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doGet(request,response);
	}

}
