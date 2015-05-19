package confRouter;


import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.Source;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerConfigurationException;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.TransformerFactoryConfigurationError;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;

import log.impl.WebLogger;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;



/**
 * Servlet implementation class Logout
 */
@WebServlet("/servlet_ConfRouter")
public class ConfRouter extends HttpServlet {
	private static final long serialVersionUID = 1L;

	/**
	 * @see HttpServlet#HttpServlet()
	 */
	public ConfRouter() {
		super();
	}

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		System.out.println("INFO: Executing servlet_ConfRouter...");

		String lgw = request.getParameter("lgw");
		String lsv = request.getParameter("lsv");
		String lnm = request.getParameter("lnm");
        
        //all the ip addresses must be valid non-zero values
		int errno = 0;
        if(!isIPv4Address(lgw) || toIPv4Address(lgw) == 0)
        	errno |= 1;
        if(!isIPv4Address(lnm) || toIPv4Address(lnm) == 0 || !isValidMask(toIPv4Address(lnm)))
        	errno |= 2;
        if(!isIPv4Address(lsv) || toIPv4Address(lsv) == 0)
        	errno |= 4;

		String wanConfType = request.getParameter("wanconf");
		String wif = null;
        String wip = null;
		String wnm = null;
		String wgw = null;
		String wdns1 = null;
		String wdns2 = null;
		
		if(wanConfType.equals("static"))
		{
			wip = request.getParameter("wip");
			wnm = request.getParameter("wnm");
			wgw = request.getParameter("wgw");
			wdns1 = request.getParameter("wdns1");
			wdns2 = request.getParameter("wdns2");

	        //all the ip addresses must be valid non-zero values
	        if(!isIPv4Address(wip) || toIPv4Address(wip) == 0)
	        	errno |= 16;
	        if(!isIPv4Address(wnm) || toIPv4Address(wnm) == 0 || !isValidMask(toIPv4Address(wnm)))
	        	errno |= 32;
	        if(!isIPv4Address(wgw) || toIPv4Address(wgw) == 0)
	        	errno |= 64;
	        if(!isIPv4Address(wdns1) || toIPv4Address(wdns1) == 0)
	        	errno |= 128;
	        if(!isIPv4Address(wdns2) || toIPv4Address(wdns2) == 0)
	        	errno |= 256;
		}
        
        if(errno == 0)
        {
        	int lgwIp = toIPv4Address(lgw);
        	int lnmIp = toIPv4Address(lnm);
        	int lsvIp = toIPv4Address(lsv);
        	//gateway and servers must have different ips in the same ip network
        	if(((lgwIp & lnmIp) != (lsvIp & lnmIp)) || (lgwIp == lsvIp))
        		errno = 8;
        	if(wanConfType.equals("static"))
        	{
            	int wipIp = toIPv4Address(wip);
            	int wnmIp = toIPv4Address(wnm);
            	int wgwIp = toIPv4Address(wgw);
            	if((wgwIp & wnmIp) != (wipIp & wnmIp))
            		errno |= 512;
        	}
        }
        if(errno != 0)
        {
        	response.getOutputStream().print(errno);
        	return;
        }

		WebLogger.getInstance().getLog().info("LAN gateway: " + lgw);
		WebLogger.getInstance().getLog().info("LAN server: " + lsv);
		WebLogger.getInstance().getLog().info("LAN netmask: " + lnm);
		WebLogger.getInstance().getLog().info("WAN conf type: " + wanConfType);
		WebLogger.getInstance().getLog().info("WAN ip: " + wip);
		WebLogger.getInstance().getLog().info("WAN netmask: " + wnm);
		WebLogger.getInstance().getLog().info("WAN gateway: " + wgw);
		WebLogger.getInstance().getLog().info("WAN DNS server 1: " + wdns1);
		WebLogger.getInstance().getLog().info("WAN DNS server 2: " + wdns2);

		// FULVIO 3/11/2013 for LIANG
		// Are you sure that it's better to use this code, with such a long path embedded?
		// I saw in other portions of the server a much cleaner way to get it:
		// String ConfPath=(String) request.getAttribute("ConfigurationFile");
		// File fileXML = new File(ConfPath+"FrogRelativePath.xml");

		File fileXML = new File((String) request.getAttribute("ConfigurationFile")+"FrogRelativePath.xml");
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

		NodeList frog_path_list = doc.getElementsByTagName("absolute_path_frog");
		Node frog_path_node = frog_path_list.item(0);
		Element frog_path_element = (Element) frog_path_node;
		NodeList frog_url_list = frog_path_element.getElementsByTagName("url").item(0).getChildNodes();
		Node frog_url_node = (Node) frog_url_list.item(0);
		
		NodeList conf_path_list = doc.getElementsByTagName("conf_path");
		Node conf_path_node = conf_path_list.item(0);
		Element conf_path_element = (Element) conf_path_node;
		NodeList conf_url_list = conf_path_element.getElementsByTagName("url").item(0).getChildNodes();
		Node conf_url_node = (Node) conf_url_list.item(0);
		
		//routerconf.xml is in absolute_path_frog/conf_path/, the path in FROG is variable
		//routerconf.xsd is in absolute_path_frog/conf/, the path in FROG is constant
		String confPath = frog_url_node.getNodeValue() + conf_url_node.getNodeValue() + "routerconf.xml";
		String schemaPath = frog_url_node.getNodeValue() + "conf/routerconf.xsd";
		
		//store LAN side settings in routerconf.xml
		try {
			File xmlfile = new File(confPath);
			if (xmlfile.exists()) {
				// Try to validate against the schema
				SchemaFactory sf = SchemaFactory
						.newInstance(javax.xml.XMLConstants.W3C_XML_SCHEMA_NS_URI);
				Schema schema = null;

				schema = sf.newSchema(new File(schemaPath));
				Source xmlfile_source = new StreamSource(xmlfile);
				Validator validator = schema.newValidator();
				validator.validate(xmlfile_source);

				// Create a new factory
				DocumentBuilderFactory factory = DocumentBuilderFactory
						.newInstance();
				// Use the factory to create builder document.
				DocumentBuilder builder = factory.newDocumentBuilder();
				builder = factory.newDocumentBuilder();
				builder.setErrorHandler(null);
				doc = builder.parse(xmlfile);
				
				Element conf_elem = doc.getDocumentElement(); // Read root element

				NodeList lanconf_list = conf_elem.getElementsByTagName("lan-config");
				Element lanconf_elem = (Element) lanconf_list.item(0); // There is only one "lan-config" element

				NodeList wanconf_list = conf_elem.getElementsByTagName("wan-config");
				Element wanconf_elem = (Element) wanconf_list.item(0); // There is only one "wan-config" element

				lanconf_elem.setAttribute("server", lsv);
				lanconf_elem.setAttribute("netmask", lnm);
				lanconf_elem.setAttribute("default_gateway", lgw);
				wanconf_elem.setAttribute("type", wanConfType.toUpperCase());
	            Transformer tr = TransformerFactory.newInstance().newTransformer();
				tr.transform(new DOMSource(doc), 
	                                 new StreamResult(new FileOutputStream(confPath)));
			}
        }
        catch(FileNotFoundException e)
        {
            e.printStackTrace();
        }
        catch(IOException e)
        {
            e.printStackTrace();
        } catch (SAXException e) {
			e.printStackTrace();
		} catch (TransformerConfigurationException e) {
			e.printStackTrace();
		} catch (TransformerFactoryConfigurationError e) {
			e.printStackTrace();
		} catch (TransformerException e) {
			e.printStackTrace();
		} catch (ParserConfigurationException e) {
			e.printStackTrace();
		}
		
		if(wanConfType.equals("static"))
		{
			//modify corresponding config files in operating system if we set static WAN side ip
			try {
	            FileWriter fostream = new FileWriter("/etc/network/interfaces");
	            BufferedWriter bw = new BufferedWriter(fostream);
	            bw.write("auto lo\niface lo inet loopback\n\n");
	            bw.write("auto " + wif + "\n");
	            bw.write("iface " + wif + " inet static\n");
	            bw.write("address " + wip + "\n");
	            bw.write("netmask " + wnm + "\n");
	            bw.write("gateway " + wgw + "\n");
	            bw.write("dns-nameservers " + wdns1 + (wdns2.equals(wdns1) ? "" : (" " + wdns2)) + "\n");
	            bw.close();
	            

	        }
	        catch(FileNotFoundException e)
	        {
	            e.printStackTrace();
	        }
	        catch(IOException e)
	        {
	            e.printStackTrace();
	        }
		}
		else if(wanConfType.equals("dhcp"))
		{
			//restore /etc/network/interfaces to what it should be like,
			//and /etc/resolv.conf can be modified after getting ip by dhcp automatically
            FileWriter fostream = new FileWriter("/etc/network/interfaces");
            BufferedWriter bw = new BufferedWriter(fostream);
            bw.write("auto lo\niface lo inet loopback\n");
            bw.close();
		}
		
		//clear /etc/resolv.conf
		FileWriter fostream = new FileWriter("/etc/resolv.conf");
		BufferedWriter bw = new BufferedWriter(fostream);
        bw.write("");
        bw.close();

    	response.getOutputStream().print("0");
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doGet(request,response);
	}
	
	private boolean isIPv4Address(String ipAddress) {
        if (ipAddress == null)
        	return false;
        String[] octets = ipAddress.split("\\.");
        if (octets.length != 4) 
            return false;

        for (int i = 0; i < 4; ++i) {
            try{
            	@SuppressWarnings("unused")
				int o = Integer.valueOf(octets[i]) << ((3-i)*8);
            } catch(NumberFormatException e){
            	return false;
            }
        }
        return true;
    }
	
	private int toIPv4Address(String ipAddress) {
        if (ipAddress == null)
        	return 0;
        String[] octets = ipAddress.split("\\.");
        if (octets.length != 4) 
            return 0;

        int ip = 0;
        for (int i = 0; i < 4; ++i) {
			ip |= Integer.valueOf(octets[i]) << ((3-i)*8);
        }
        return ip;
    }

	private boolean isValidMask(int ip)
	{
		int mask = 0;
		for(int i=31; i>=0; i--)
		{
			mask |= 1 << i;
			if(ip == mask)
				return true;
		}
		return false;
	}

}
