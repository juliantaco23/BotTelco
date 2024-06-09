import React, {useState} from "react";
import axios from "axios";
import {useNavigate} from "react-router-dom";
import "../styles.css";

const RegisterForm = () => {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [errorMessage, setErrorMessage] = useState("");
  const backendUrl = process.env.REACT_APP_BACKEND_URL;
	const navigate = useNavigate();

	const handleSubmit = async (event) => {
		event.preventDefault();

		try {
      const response = await axios.post(`${backendUrl}/register`,
				{username, password}
			);

			if (response.data.message === "User registered successfully") {
				setUsername("");
				setPassword("");
				navigate("/");
			} else {
				setErrorMessage(response.data.message);
			}
		} catch (error) {
			console.error(error);
			setErrorMessage("An error occurred. Please try again later.");
		}
	};

	return (
		<div className="register-container">
			<div className="register-box">
				<h2>Register</h2>
				<form onSubmit={handleSubmit}>
					<label htmlFor="username">Username:</label>
					<input
						type="text"
						id="username"
						name="username"
						value={username}
						onChange={(e) => setUsername(e.target.value)}
					/>

					<label htmlFor="password">Password:</label>
					<input
						type="password"
						id="password"
						name="password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
					/>

					<button type="submit">Register</button>
				</form>
				{errorMessage && (
					<p className="error-message">{errorMessage}</p>
				)}
			</div>
		</div>
	);
};

export default RegisterForm;
