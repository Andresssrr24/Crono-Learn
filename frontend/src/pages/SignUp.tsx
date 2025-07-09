import { Link } from "react-router-dom"
import { Register } from "../components/user_auth/Register"

export function SignUpPage() {
    return (
        <div>
            <Link to={'/'}>CRONOLEARN</Link>
            <Register />
        </div>
    )
}