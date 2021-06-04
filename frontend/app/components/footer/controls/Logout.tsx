import React from "react";
import styled from "styled-components";
import { LogOut } from "../../../icons/LogOut";
import { useRouter } from "next/router";
import { useSpotify } from "../../../context/spotify/SpotifyContext";

const LogoutButton = styled.button``;

const LogoutIcon = styled(LogOut)`
    width: 2.4rem;
    height: 2.4rem;
`;

export const Logout: React.FC = () => {
    const router = useRouter();
    const { authToken } = useSpotify();

    const logout = async () => {
        await fetch("/api/logout");
        router.replace("/");
    };

    if (!authToken) return null;

    return (
        <LogoutButton onClick={logout}>
            <LogoutIcon />
        </LogoutButton>
    );
};