package confRouter;


import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
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
@WebServlet("/servlet_GetRouterConf")
public class GetRouterConf extends HttpServlet {
	private static final long serialVersionUID = 1L;

	/**
	 * @see HttpServlet#HttpServlet()
	 */
	public GetRouterConf() {
		super();
	}

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		System.out.println("INFO: Executing servlet_GetRouterConf...");

		String lgw = null;
		String lsv = null;
		String lnm = null;
		String wanConfType = null;
		String wif = null;
        String wip = null;
		String wnm = null;
		String wgw = null;
		String wdns1 = null;
		String wdns2 = null;

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
		WebLogger.getInstance().getLog().info("conf file: " + confPath);
		
		//read routerconf.xml to get LAN side parameters, WAN side interface
		//and WAN side ip allocating method

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

				lsv = lanconf_elem.getAttribute("server");
				lnm = lanconf_elem.getAttribute("netmask");
				lgw = lanconf_elem.getAttribute("default_gateway");

				NodeList wanconf_list = conf_elem.getElementsByTagName("wan-config");
				Element wanconf_elem = (Element) wanconf_list.item(0); // There is only one "wan-config" element

				wif = wanconf_elem.getAttribute("interface");
				wanConfType = wanconf_elem.getAttribute("type");

	            if(wanConfType.equals("STATIC"))
	            {
	            	//if use static ip, read corresponding config files in operation system
	            	//for WAN side interface addresses
	            	FileInputStream fistream = new FileInputStream("/etc/network/interfaces");
	                DataInputStream in = new DataInputStream(fistream);
	                BufferedReader br = new BufferedReader(new InputStreamReader(in));
	                
	                boolean wifInfo = false;
	                String strLine = null;
					while((strLine = br.readLine()) != null)
	                {
	                    String[] substr = strLine.split("[ ]");
	                    if(substr[0].equals("auto") && substr[1].equals(wif))
	                    {
	                    	wifInfo = true;
	                    }
	                    else if(wifInfo)
	                    {
	                    	if(substr[0].equals("address"))
	                        {
	                        	wip = substr[1];
	                        }
	                        else if(substr[0].equals("netmask"))
	                        {
	                          	wnm = substr[1];
	                        }
	                        else if(substr[0].equals("gateway"))
	                        {
	                          	wgw = substr[1];
	                        }
	                    }
	                }
	                br.close();
	                
	                //for DNS server address
	                fistream = new FileInputStream("/etc/resolv.conf");
	                in = new DataInputStream(fistream);
	                br = new BufferedReader(new InputStreamReader(in));
	                
	                while((strLine = br.readLine()) != null)
	                {
	                    String[] substr = strLine.split("[ ]");
	                    if(substr[0].equals("nameserver") && !substr[1].startsWith("127"))
	                    {
	                    	if(wdns1 == null)
	                    		wdns1 = substr[1];
	                    	else if(wdns2 == null)
	                    		wdns2 = substr[1];
	                    }
	                }
	                if(wdns2 == null)
	            		wdns2 = wdns1;
	                br.close();
	            }
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
		} catch (ParserConfigurationException e) {
			e.printStackTrace();
		}

		WebLogger.getInstance().getLog().info("wan interface: " + wif);
		WebLogger.getInstance().getLog().info("LAN gateway: " + lgw);
		WebLogger.getInstance().getLog().info("LAN server: " + lsv);
		WebLogger.getInstance().getLog().info("LAN netmask: " + lnm);
		WebLogger.getInstance().getLog().info("WAN conf type: " + wanConfType);
		WebLogger.getInstance().getLog().info("WAN ip: " + wip);
		WebLogger.getInstance().getLog().info("WAN netmask: " + wnm);
		WebLogger.getInstance().getLog().info("WAN gateway: " + wgw);
		WebLogger.getInstance().getLog().info("WAN DNS server 1: " + wdns1);
		WebLogger.getInstance().getLog().info("WAN DNS server 2: " + wdns2);
		 
		response.getOutputStream().print(lsv + "&" + lnm + "&" + lgw + "&" + wanConfType.toLowerCase() +
				(wanConfType.equals("STATIC") ? "&" + wip + "&" + wnm + "&" + wgw + "&" + wdns1 + "&" + wdns2 : ""));
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doGet(request,response);
	}

}
