package utils.login;

import java.util.Properties;

import javax.mail.*;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeMessage;

public class MailUtility {


	public static synchronized void sendMail (String dest, String IDTempUser) {


		PasswordAuthentication authenticator = new javax.mail.PasswordAuthentication("config.cntrl","openflow");

		// Get system properties
		Properties properties = System.getProperties();

		// Setup mail server
		properties.setProperty("mail.smtp.host", "smtp.gmail.com");
		properties.put("mail.smtp.port", "465");
		//properties.put("mail.smtp.port", "587");
		properties.setProperty("mail.smtp.auth", "true");
		properties.put("mail.smtp.ssl.enable", "true");
		//properties.put("mail.smtp.starttls.enable", "true");
		properties.put("mail.smtp.username", "config.cntrl");
		properties.put("mail.smtp.password", "openflow");

		properties.setProperty("mail.smtp.submitter", authenticator.getUserName());

		Session session = Session.getInstance(properties,
				new javax.mail.Authenticator() {
			protected PasswordAuthentication getPasswordAuthentication() {
				return new PasswordAuthentication("config.cntrl", "openflow");
			}
		});

		// Get the default Session object.
		//Session session = Session.getDefaultInstance(properties);
		session.setDebug(true);

		try {



			// Create a default MimeMessage object.
			MimeMessage message = new MimeMessage(session);

			String messageBody="Your account has been created click " +
					"<a href=\"http://goto.myfrog/confirmReg?userid="+ IDTempUser+"\">here</a> to confirm your email address.";
			// Fill the message
			message.setContent(message, "text/html"); 

			// Put parts in message
			message.setText(messageBody); 
			message.setContent(messageBody,"text/html");
			message.setFrom(new InternetAddress("config.cntrl@gmail.com"));

			message.addRecipient(Message.RecipientType.TO, new InternetAddress(dest));

			message.setSubject("Confirm your email address");


			Transport.send(message);

			System.out.println("Sent message successfully....");

		} catch (MessagingException mex) {
			mex.printStackTrace();
		}
	}
}
