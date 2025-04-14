import React, { useEffect, useState } from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell, { tableCellClasses } from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import { styled } from '@mui/material/styles';
import Typography from '@mui/material/Typography';

const StyledTableCell = styled(TableCell)(({ theme }) => ({
    [`&.${tableCellClasses.head}`]: {
        backgroundColor: "#c8ffff",
        color: '#0077C2',
    },
    [`&.${tableCellClasses.body}`]: {
        fontSize: 14,
    },
}));

export default function FaultAlarmTable({ faultAlarms }) {
    return (
        <>
            <Typography sx={{mt: 5}} variant="h4" gutterBottom>
                ⚠️ Live Fault Alerts
            </Typography>
            <TableContainer component={Paper}>
                <Table sx={{ minWidth: 650 }} aria-label="Alarm Table">
                    <TableHead>
                        <TableRow>
                            <StyledTableCell>Room No.</StyledTableCell>
                            <StyledTableCell align="right">Device Type</StyledTableCell>
                            <StyledTableCell align="right">Fault Status</StyledTableCell>
                            <StyledTableCell align="right">Fault Type</StyledTableCell>
                            <StyledTableCell align="right">Fault Time</StyledTableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {faultAlarms.map((row, idx) => (
                            <TableRow key={idx}>
                                <TableCell component="th" scope="row">{row.room}</TableCell>
                                <TableCell align="right">{row.device_type}</TableCell>
                                <TableCell align="right">{row.fault_status}</TableCell>
                                <TableCell align="right">{row.fault_type}</TableCell>
                                <TableCell align="right">{row.fault_time}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </>
    );
}
